#!/bin/sh
set -eu

usage() {
  printf '%s\n' "Usage: $0 [peer-repository-root] [expected-status]" >&2
  exit 2
}

case "$#" in
  0) expected_status="pending" ;;
  1) peer_root=$1; expected_status="pending" ;;
  2) peer_root=$1; expected_status=$2 ;;
  *) usage ;;
esac

self_root=$(CDPATH= cd -- "$(dirname -- "$0")/../.." && pwd)
if [ "${peer_root+x}" != x ]; then
  case "$(basename -- "$self_root")" in
    NEW-Utell-phone) peer_root="$self_root/../NEW-Utell-server" ;;
    NEW-Utell-server) peer_root="$self_root/../NEW-Utell-phone" ;;
    *)
      printf '%s\n' "Cannot infer peer repository; pass its root as the first argument." >&2
      exit 2
      ;;
  esac
fi
peer_root=$(CDPATH= cd -- "$peer_root" && pwd)

profile="$self_root/harness/契约/integration-profile.yaml"
peer_profile="$peer_root/harness/契约/integration-profile.yaml"
harness_config="$self_root/harness/harness.yaml"
scenario_catalog="$self_root/harness/scenarios/catalog.yaml"

[ -f "$profile" ] || { printf '%s\n' "Missing profile: $profile" >&2; exit 1; }
[ -f "$peer_profile" ] || { printf '%s\n' "Missing peer profile: $peer_profile" >&2; exit 1; }
[ -f "$harness_config" ] || { printf '%s\n' "Missing harness config: $harness_config" >&2; exit 1; }
[ -f "$scenario_catalog" ] || { printf '%s\n' "Missing scenario catalog: $scenario_catalog" >&2; exit 1; }

cmp -s "$profile" "$peer_profile" || {
  printf '%s\n' "FAIL: integration profiles differ byte-for-byte" >&2
  diff -u "$profile" "$peer_profile" >&2 || true
  exit 1
}

ruby - "$profile" "$harness_config" "$scenario_catalog" "$self_root" "$expected_status" <<'RUBY'
require "yaml"

path, harness_path, catalog_path, repository_root, expected_status = ARGV
profile = YAML.load_file(path)
abort "profile must be a mapping" unless profile.is_a?(Hash)

required = %w[profile_version status owner canonical_path repositories source_documents gates sections e2ee confirmed_invariants compatibility]
missing = required.reject { |key| profile.key?(key) }
abort "missing top-level keys: #{missing.join(', ')}" unless missing.empty?

abort "unexpected status #{profile.fetch('status').inspect}; expected #{expected_status.inspect}" unless profile.fetch("status") == expected_status
abort "profile_version must be a 0.x or 1.x semver" unless profile.fetch("profile_version").match?(/\A\d+\.\d+\.\d+\z/)
abort "repositories must name both repositories" unless profile.fetch("repositories").sort == %w[NEW-Utell-phone NEW-Utell-server]
abort "canonical_path mismatch" unless profile.fetch("canonical_path") == "harness/契约/integration-profile.yaml"

compatibility = profile.fetch("compatibility")
abort "byte_identical_across_repositories must remain true" unless compatibility.fetch("byte_identical_across_repositories") == true

if %w[pending proposed].include?(profile.fetch("status"))
  abort "production implementation is not allowed before approval" unless compatibility.fetch("production_implementation_allowed") == false
end

sections = profile.fetch("sections")
abort "sections must be a mapping" unless sections.is_a?(Hash) && !sections.empty?
allowed = %w[pending proposed approved deprecated]
invalid = sections.values.reject { |value| allowed.include?(value) }
abort "invalid section status: #{invalid.inspect}" unless invalid.empty?

harness = YAML.load_file(harness_path)
catalog = YAML.load_file(catalog_path)
required_scenarios = harness.dig("required_scenarios")
abort "harness.required_scenarios must be a non-empty array" unless required_scenarios.is_a?(Array) && !required_scenarios.empty?
abort "scenario catalog must be a mapping" unless catalog.is_a?(Hash)
catalog_scenarios = catalog.fetch("scenarios")
abort "scenario catalog must contain a scenarios array" unless catalog_scenarios.is_a?(Array)
abort "scenario catalog status must be planned, ready or blocked" unless %w[planned ready blocked].include?(catalog.fetch("status"))

keys = catalog_scenarios.map { |scenario| scenario.fetch("key") }
duplicates = keys.group_by(&:itself).select { |_key, values| values.length > 1 }.keys
abort "duplicate scenario keys: #{duplicates.join(', ')}" unless duplicates.empty?
missing_scenarios = required_scenarios - keys
abort "required scenarios missing from catalog: #{missing_scenarios.join(', ')}" unless missing_scenarios.empty?

scenario_statuses = %w[planned ready blocked]
invalid_scenario_statuses = catalog_scenarios.map { |scenario| scenario.fetch("status") }.reject { |value| scenario_statuses.include?(value) }
abort "invalid scenario status: #{invalid_scenario_statuses.inspect}" unless invalid_scenario_statuses.empty?
catalog_scenarios.each do |scenario|
  abort "scenario id must use SC-XX-YYYY-NNN" unless scenario.fetch("id").match?(/\ASC-[A-Z]{2}-\d{4}-\d{3}\z/)
  abort "scenario requires must be a non-empty array" unless scenario.fetch("requires").is_a?(Array) && !scenario.fetch("requires").empty?
  if scenario.fetch("status") == "ready"
    abort "ready scenario must declare a fixture" unless scenario.key?("fixture")
    abort "ready scenario must declare a runner" unless scenario.key?("runner")
    abort "missing ready scenario fixture" unless File.file?(File.expand_path(scenario.fetch("fixture"), repository_root))
    abort "missing ready scenario runner" unless File.file?(File.expand_path(scenario.fetch("runner"), repository_root))
  end
end
section_names = sections.keys
invalid_dependencies = catalog_scenarios.flat_map { |scenario| scenario.fetch("requires") }.uniq - section_names
abort "scenario dependencies missing from profile sections: #{invalid_dependencies.join(', ')}" unless invalid_dependencies.empty?

puts "profile_gate=passed"
puts "status=#{profile.fetch('status')}"
puts "profile_version=#{profile.fetch('profile_version')}"
puts "sections=#{sections.length}"
puts "scenarios=#{catalog_scenarios.length}"
RUBY

profile_sha=$(shasum -a 256 "$profile" | awk '{print $1}')
printf 'profile_sha256=%s\n' "$profile_sha"
printf 'peer_repository=%s\n' "$peer_root"
