#!/usr/bin/env ruby
# Assemble complete print sources, including the contents of multi-document archives.
require 'cgi'
require 'digest'
require 'fileutils'
require 'json'
require 'nokogiri'
require 'optparse'
require 'open3'
require 'pathname'
require 'uri'

options = {site: '_site', manifest: File.join(__dir__, 'pdf-manifest.json'), preview: 'http://127.0.0.1:4175', server: 'http://127.0.0.1:4180'}
OptionParser.new do |parser|
  parser.on('--site PATH') { |v| options[:site] = v }
  parser.on('--manifest PATH') { |v| options[:manifest] = v }
  parser.on('--output PATH') { |v| options[:output] = v }
  parser.on('--preview URL') { |v| options[:preview] = v }
  parser.on('--server URL') { |v| options[:server] = v }
end.parse!
abort 'Specify --output with a temporary directory to serve print sources' unless options[:output]
root = Pathname.new(options[:site]).expand_path
target = Pathname.new(options[:output]).expand_path
FileUtils.mkdir_p(target)
manifest = JSON.parse(File.read(options[:manifest]))
jobs = []
manifest.fetch('documents').each_with_index do |item, index|
  next if item['retain_original'] || item.fetch('sources').empty?
  if item['print_layout'] == 'schedule'
    repository = Pathname.new(__dir__).join('../..').expand_path
    program = "import pathlib,sys; sys.path.insert(0,sys.argv[1]); from schedule_html import render_print; p=pathlib.Path(sys.argv[2]); print(render_print(p.read_text(),p))"
    html, errors, status = Open3.capture3('python3', '-c', program, repository.join('scripts/schedule').to_s, repository.join('schedule.tex').to_s)
    raise "Schedule print rendering failed: #{errors}" unless status.success?
    filename = format('document-%03d.html', index)
    File.write(target.join(filename), html)
    jobs << {pdf: item['pdf'], url: options[:server] + '/' + filename,
             source_urls: item['sources'], source_sha256: Digest::SHA256.hexdigest(html),
             original_sha256: item['original_sha256'], parts: 1, native_math: 0, landscape: true}
    next
  end
  documents = item.fetch('sources').map do |source|
    source_path = root.join(source.delete_prefix('/'))
    source_path = source_path.join('index.html') if source_path.directory?
    raise "Missing HTML companion: #{source_path}" unless source_path.file?
    [source, source_path, Nokogiri::HTML5(File.read(source_path))]
  end
  template = documents.first.last.dup
  main = template.at_css('main') or raise "Missing main in #{item['pdf']}"
  sections = []
  documents.each_with_index do |(source, _path, doc), part|
    content = doc.at_css('main .row-offcanvas > .col-md-8') || doc.at_css('main')
    raise "Missing document content in #{source}" unless content
    content.css('nav[aria-label="Breadcrumb"],nav[aria-label="Page navigation"]').remove
    content.css('nav').remove if part.positive?
    origin = options[:preview] + URI::DEFAULT_PARSER.escape(source, /[^\x21-\x7e]|[<>"{}|\\^`]/)
    content.css('[src],a[href]').each do |node|
      attribute = node.name == 'a' ? 'href' : 'src'
      value = node[attribute]
      next unless value
      escaped = URI::DEFAULT_PARSER.escape(value, /[^\x21-\x7e]|[<>"{}|\\^`]/)
      node[attribute] = URI.join(origin, escaped).to_s
    end
    if documents.length > 1
      ids = content.css('[id]').map { |node| node['id'] }
      content.css('[aria-labelledby],[aria-describedby],[headers],[for]').each do |node|
        %w[aria-labelledby aria-describedby headers for].each do |attribute|
          next unless node[attribute]
          node[attribute] = node[attribute].split.map { |id| ids.include?(id) ? "part-#{part}-#{id}" : id }.join(' ')
        end
      end
      content.css('[id]').each { |node| node['id'] = "part-#{part}-#{node['id']}" }
      if part.positive?
        content.css('h1,h2,h3,h4,h5').each { |node| node.name = "h#{node.name[1].to_i + 1}" }
        sections << "<section style=\"break-before:page\">#{content.inner_html}</section>"
      else
        sections << content.inner_html
      end
    else
      sections << content.inner_html
    end
  end
  main.inner_html = sections.join("\n")
  main['class'] = 'container document-content'
  base = Nokogiri::XML::Node.new('base', template)
  base['href'] = options[:preview] + documents.first.first
  template.at_css('head').prepend_child(base)
  stylesheet = Nokogiri::XML::Node.new('link', template)
  stylesheet['rel'] = 'stylesheet'
  stylesheet['href'] = options[:preview] + '/css/documents.css'
  template.at_css('head').add_child(stylesheet)
  filename = format('document-%03d.html', index)
  html = template.to_html
  File.write(target.join(filename), html)
  # Header/footer navigation is removed by the exporter and must not invalidate
  # every PDF when unrelated pages are added. Hash all actual print inputs.
  assets = %w[css/main.css css/documents.css css/syntax.css assets/js/document-forms.js assets/js/math-accessibility.js].map do |asset|
    file = root.join(asset)
    [asset, file.file? ? Digest::SHA256.file(file).hexdigest : nil]
  end
  main.css('img[src]').each do |node|
    uri = URI(node['src'])
    next unless uri.host == URI(options[:preview]).host
    asset = URI::DEFAULT_PARSER.unescape(uri.path).delete_prefix('/')
    file = root.join(asset)
    raise "Missing print image: #{asset}" unless file.file?
    assets << [asset, Digest::SHA256.file(file).hexdigest]
  end
  print_hash = Digest::SHA256.hexdigest(JSON.generate([template.at_css('head').inner_html, main.to_html, assets]))
  jobs << {pdf: item['pdf'], url: options[:server] + '/' + filename,
           source_urls: item['sources'], source_sha256: print_hash,
           original_sha256: item['original_sha256'], parts: documents.length,
           native_math: main.css('math').size}
end
File.write(target.join('jobs.json'), JSON.pretty_generate(jobs) + "\n")
puts JSON.generate({jobs: jobs.size, directory: target.to_s})
