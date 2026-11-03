# Detect duplicate settings before YAML silently keeps only the last value.
require "psych"

errors = []
paths = ["_config.yml", *Dir["_posts/*.md"], *Dir["*.md"], *Dir[".github/workflows/*.yml"]]
paths.each do |path|
  content = File.read(path)
  if path.end_with?(".md")
    match = content.match(/\A---\s*\n(.*?)\n---/m)
    next unless match
    content = match[1]
  end
  visit = lambda do |node|
    if node.is_a?(Psych::Nodes::Mapping)
      seen = []
      node.children.each_slice(2) do |key, _value|
        errors << "#{path}: duplicate setting #{key.value.inspect}" if seen.include?(key.value)
        seen << key.value
      end
    end
    (node.children || []).each { |child| visit.call(child) }
  end
  begin
    visit.call(Psych.parse_stream(content))
  rescue Psych::SyntaxError => error
    errors << "#{path}: #{error.message}"
  end
end
abort errors.join("\n") unless errors.empty?
puts "YAML syntax and duplicate-setting checks passed."
