#!/usr/bin/env ruby
# frozen_string_literal: true

require "json"

fixture_path = ARGV.fetch(0, File.expand_path("../fixtures/pairing_expired_or_replayed.json", __dir__))
fixture = JSON.parse(File.read(fixture_path))

abort "fixture_version must be 0.1" unless fixture.fetch("fixture_version") == "0.1"
abort "unexpected scenario key" unless fixture.fetch("scenario_key") == "pairing_expired_or_replayed"
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
abort "fixture must contain exactly two cases" unless cases.length == 2
expected_names = %w[expired_token replayed_token]
abort "fixture must cover expired and replayed token cases" unless cases.map { |example| example.fetch("name") }.sort == expected_names.sort

cases.each do |example|
  abort "pairing attempt must be present" unless example.fetch("pairing_attempted") == true
  invalid_conditions = [example.fetch("token_expired"), example.fetch("token_already_used")].count(true)
  abort "case #{example.fetch('name')} must have exactly one invalid token condition" unless invalid_conditions == 1
  abort "invalid token must map to PAIRING_INVALID" unless example.fetch("expected_error") == "PAIRING_INVALID"
  abort "Relay must not establish invalid pairing" unless example.fetch("pairing_established") == false
  abort "Relay must not start a handshake for invalid pairing" unless example.fetch("handshake_started") == false
  abort "invalid pairing must not be routeable" unless example.fetch("route_allowed") == false
  abort "invalid pairing must not mutate pairing state" unless example.fetch("pairing_state_mutated") == false
  abort "Relay must not persist business payload" unless example.fetch("business_payload_persisted_by_relay") == false
end

puts "pairing_expired_or_replayed_semantics=passed"
puts "cases=#{cases.length}"
puts "business_data=false"
