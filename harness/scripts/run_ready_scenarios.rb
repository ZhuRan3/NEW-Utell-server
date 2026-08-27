#!/usr/bin/env ruby
# frozen_string_literal: true

require "pathname"
require "rbconfig"
require "yaml"

repository_root = File.expand_path("../..", __dir__)
gate_path = File.join(repository_root, "harness/scripts/verify_contract_gate.sh")
catalog_path = File.join(repository_root, "harness/scenarios/catalog.yaml")

abort "contract gate failed" unless system("sh", gate_path)

catalog = YAML.load_file(catalog_path)
scenarios = catalog.fetch("scenarios")
ready_scenarios = scenarios.select { |scenario| scenario.fetch("status") == "ready" }
abort "catalog must contain at least one ready scenario" if ready_scenarios.empty?

resolve_file = lambda do |relative_path, label|
  abort "#{label} path must be relative" if Pathname.new(relative_path).absolute?

  resolved = File.expand_path(relative_path, repository_root)
  root_prefix = "#{repository_root}#{File::SEPARATOR}"
  abort "#{label} escapes repository root: #{relative_path}" unless resolved.start_with?(root_prefix)
  abort "missing #{label}: #{relative_path}" unless File.file?(resolved)

  resolved
end

ready_scenarios.each do |scenario|
  id = scenario.fetch("id")
  fixture_path = resolve_file.call(scenario.fetch("fixture"), "fixture")
  runner_path = resolve_file.call(scenario.fetch("runner"), "runner")
  command = case File.extname(runner_path)
            when ".rb"
              [RbConfig.ruby, runner_path, fixture_path]
            when ".sh"
              ["sh", runner_path, fixture_path]
            else
              abort "unsupported runner type for #{id}: #{runner_path}"
            end

  puts "scenario_start=#{id}"
  abort "scenario failed: #{id}" unless system(*command)
  puts "scenario_passed=#{id}"
end

puts "ready_scenarios=passed"
puts "ready_count=#{ready_scenarios.length}"
