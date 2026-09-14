# Index rendered page content so search never exposes Liquid, CSS, or scripts.
require 'json'
require 'nokogiri'

Jekyll::Hooks.register :site, :post_render do |site|
  index = site.pages.find { |page| page.url == '/search-index.json' }
  next unless index

  people = site.collections['departmentpeople']&.docs || []
  entries = (site.pages + site.posts.docs + people).filter_map do |item|
    data = item.data
    next if data['search_exclude'] || data['redirect_to'] || data['published'] == false
    next if item.url.match?(%r{\A/allnews/page\d+})
    next unless item.output.to_s.match?(/<html\b/i)
    doc = Nokogiri::HTML(item.output)
    next if doc.at_css('meta[http-equiv="refresh"]')
    content = doc.at_css('main')
    next unless content
    title = if data['lastname']
              [data['name'], data['lastname']].compact.join(' ')
            else
              data['title'] || content.at_css('h1')&.text
            end
    next if title.to_s.strip.empty?
    content.css('script,style,nav,noscript,annotation,[hidden],[aria-hidden="true"],.visually-hidden').remove
    # Keep word boundaries between headings, paragraphs, and table cells.
    content.css('p,li,h1,h2,h3,h4,h5,h6,td,th,dt,dd,br').each { |node| node.add_next_sibling(' ') }
    {title: title.gsub(/\s+/, ' ').strip, url: item.url,
     text: content.text.gsub(/\s+/, ' ').strip}
  end
  index.output = JSON.generate(entries.uniq { |entry| entry[:url] }) + "\n"
end
