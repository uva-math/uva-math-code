#!/usr/bin/env ruby
# Structural regression checks. These do not certify WCAG conformance.
require 'nokogiri'
require 'json'
require 'pathname'

root = Pathname.new(ARGV[0] || '_site').expand_path
report_path = ARGV[1]
issues = []
count = 0
Dir.glob(root.join('**/*.html')).sort.each do |filename|
  source = File.read(filename)
  next unless source.match?(/<html\b/i)
  doc = Nokogiri::HTML5(source)
  next if doc.at_css('meta[http-equiv="refresh"]')
  next unless doc.at_css('html') && doc.at_css('body')
  path = Pathname.new(filename).relative_path_from(root).to_s
  next if path.start_with?('docs/', 'reports/', 'scripts/')
  count += 1
  add = ->(rule, node, detail) { issues << {path: path, rule: rule, line: node&.line, detail: detail} }
  titles = doc.css('head title')
  add.call('document-title', doc.at_css('head'), 'Exactly one nonempty title is required') unless titles.length == 1 && !titles.first.text.strip.empty?
  add.call('html-lang', doc.at_css('html'), 'Missing document language') if doc.at_css('html')['lang'].to_s.empty?
  main = doc.css('main')
  add.call('main', doc.at_css('body'), 'Exactly one main landmark is required') unless main.length == 1
  add.call('skip-link', doc.at_css('body'), 'Missing skip link to main content') unless doc.at_css('a[href="#main-content"]') && doc.at_css('#main-content')
  h1s = doc.css('h1')
  add.call('h1', h1s.first || doc.at_css('body'), "Expected one h1; found #{h1s.length}") unless h1s.length == 1
  previous = 0
  doc.css('h1,h2,h3,h4,h5,h6').each do |node|
    level = node.name[1].to_i
    add.call('empty-heading', node, 'Heading has no text') if node.text.strip.empty?
    add.call('heading-order', node, "h#{previous} to h#{level}: #{node.text.strip[0,100]}") if level > previous + 1
    previous = level
  end
  doc.css('[id]').group_by { |n| n['id'] }.each do |id, nodes|
    add.call('duplicate-id', nodes.first, id) if nodes.length > 1 && !id.empty?
  end
  doc.css('img').each do |node|
    add.call('image-alt', node, node['src']) unless node.key?('alt')
    add.call('redundant-title', node, node['alt']) if node['title'] && node['title'] == node['alt']
  end
  doc.css('iframe').each { |n| add.call('frame-title', n, n['src']) if n['title'].to_s.strip.empty? }
  doc.css('math').each do |math|
    annotation = math.at_css('annotation[encoding="application/x-tex"]')
    if annotation && math['aria-label'] && math['aria-label'].strip == annotation.text.strip
      add.call('math-label', math, 'Raw TeX label overrides native mathematical structure')
    end
    math.css('mi,mn,mo,mtext,ms').each do |token|
      if token.element_children.any? { |child| !%w[mglyph malignmark].include?(child.name) }
        add.call('math-token', token, 'MathML token contains nested mathematical elements')
      end
    end
  end
  doc.css('ul,ol').each do |list|
    list.element_children.each do |child|
      add.call('list-structure', child, "#{child.name} must be inside a list item") unless %w[li script template].include?(child.name)
    end
  end
  doc.css('li').each do |item|
    add.call('list-item', item, 'List item needs a list parent') unless %w[ul ol].include?(item.parent.name)
  end
  doc.css('details').each do |details|
    summary = details.element_children.find { |child| child.name == 'summary' }
    add.call('disclosure-name', details, 'Details needs a visible, descriptive summary') unless summary && !summary.text.strip.empty?
  end
  doc.css('input:not([type="hidden"]),select,textarea').each do |n|
    next if %w[submit button reset].include?(n['type']) && !n['value'].to_s.empty?
    labeled = n['aria-label'] || n['aria-labelledby'] || n.ancestors('label').any? || doc.css('label').any? { |l| l['for'] && l['for'] == n['id'] }
    add.call('form-label', n, n['id'] || n['name']) unless labeled
  end
  doc.css('a[href],button').each do |n|
    label = n.text.strip + n.css('img').map { |i| i['alt'].to_s }.join
    add.call('control-name', n, n['href'] || n.name) if label.empty? && !n['aria-label'] && !n['aria-labelledby'] && n['aria-hidden'] != 'true'
    add.call('new-window', n, n['href']) if n['target'] == '_blank'
  end
end
report = {pages: count, issues: issues, counts: issues.group_by { |i| i[:rule] }.transform_values(&:length)}
File.write(report_path, JSON.pretty_generate(report) + "\n") if report_path
puts JSON.pretty_generate({pages: count, issues: issues.length, counts: report[:counts]})
exit(issues.empty? ? 0 : 1)
