#!/usr/bin/env ruby
# frozen_string_literal: true

require "json"

fixture_path = ARGV.fetch(0, File.expand_path("../fixtures/primary_connector_only.json", __dir__))
fixture = JSON.parse(File.read(fixture_path))

abort "fixture_version must be 0.1" unless fixture.fetch("fixture_version") == "0.1"
abort "unexpected scenario key" unless fixture.fetch("scenario_key") == "primary_connector_only"
abort "fixture must not contain business data" unless fixture.fetch("contains_business_data") == false

forbidden_keys = %w[raw_text capture_text title summary capture_id log_entry_id private_key plaintext]
walk = lambda do |value|
  case value
  when Hash
    value.each do |key, child|
      abort "fixture contains forbidden field #{key}" if forbidden_keys.include?(key)
      walk.call(child)
    end
  when Array
    value.each { |child| walk.call(child) }
  end
end
walk.call(fixture)

cases = fixture.fetch("cases")
abort "fixture must contain exactly three cases" unless cases.length == 3
expected_names = %w[single_primary_allows_route second_connector_without_revoke_rejected explicit_revoke_then_replace]
abort "fixture must cover single-primary cases" unless cases.map { |example| example.fetch("name") }.sort == expected_names.sort

cases.each do |example|
  abort "active primary count must be one before the operation" unless example.fetch("active_primary_count_before") == 1
  abort "active primary count must be one after the operation" unless example.fetch("active_primary_count_after") == 1
  abort "more than one connector must never be routeable" if example.fetch("old_primary_route_allowed") && example.fetch("new_connector_route_allowed")

  if example.fetch("name") == "single_primary_allows_route"
    abort "baseline case must not attempt a replacement" unless example.fetch("new_connector_pairing_attempted") == false
    abort "baseline case must preserve pairing state" unless example.fetch("pairing_state_mutated") == false
  elsif example.fetch("name") == "second_connector_without_revoke_rejected"
    abort "second connector must be rejected without explicit revoke" unless example.fetch("new_pairing_established") == false
    abort "old primary must remain routeable" unless example.fetch("old_primary_route_allowed") == true
    abort "rejected replacement must not mutate pairing state" unless example.fetch("pairing_state_mutated") == false
  else
    abort "replacement must be explicitly requested" unless example.fetch("replacement_explicitly_requested") == true
    abort "replacement must revoke the old pairing" unless example.fetch("old_pairing_revoked") == true
    abort "replacement must establish the new pairing" unless example.fetch("new_pairing_established") == true
    abort "old primary must stop routing after replacement" unless example.fetch("old_primary_route_allowed") == false
    abort "new primary must be routeable after replacement" unless example.fetch("new_connector_route_allowed") == true
    abort "replacement must mutate pairing state" unless example.fetch("pairing_state_mutated") == true
  end
end

puts "primary_connector_only_semantics=passed"
puts "cases=#{cases.length}"
puts "business_data=false"
