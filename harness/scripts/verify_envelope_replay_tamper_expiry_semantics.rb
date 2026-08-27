#!/usr/bin/env ruby
# frozen_string_literal: true

require "json"

fixture_path = ARGV.fetch(0, File.expand_path("../fixtures/envelope_replay_tamper_expiry.json", __dir__))
fixture = JSON.parse(File.read(fixture_path))

abort "fixture_version must be 0.1" unless fixture.fetch("fixture_version") == "0.1"
abort "unexpected scenario key" unless fixture.fetch("scenario_key") == "envelope_replay_tamper_expiry"
abort "fixture must not contain business data" unless fixture.fetch("contains_business_data") == false
abort "public error mapping must remain explicitly unfrozen" unless fixture.fetch("public_error_mapping_frozen") == false

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
expected_names = %w[duplicate_sequence_replay invalid_integrity_tamper expired_envelope]
abort "fixture must cover replay, tamper and expiry exactly once" unless cases.map { |example| example.fetch("name") }.sort == expected_names.sort

cases.each do |example|
  sequence_relation = example.fetch("sequence_relation")
  integrity_valid = example.fetch("integrity_valid")
  expired = example.fetch("expired")
  invalid_conditions = [sequence_relation == "duplicate", integrity_valid == false, expired].count(true)
  abort "case #{example.fetch('name')} must have exactly one rejection cause" unless invalid_conditions == 1
  abort "replay/tamper/expiry envelope must be rejected" unless example.fetch("envelope_rejected") == true
  abort "rejected envelope must not be routed" unless example.fetch("route_allowed") == false
  abort "Relay must not persist business payload" unless example.fetch("business_payload_persisted_by_relay") == false
  abort "unfrozen public mapping must not invent an error code" unless example.fetch("public_error_code").nil?
end

puts "envelope_replay_tamper_expiry_semantics=passed"
puts "cases=#{cases.length}"
puts "business_data=false"
