#!/usr/bin/env ruby
# frozen_string_literal: true

require "json"

fixture_path = ARGV.fetch(0, File.expand_path("../fixtures/revocation.json", __dir__))
fixture = JSON.parse(File.read(fixture_path))

abort "fixture_version must be 0.1" unless fixture.fetch("fixture_version") == "0.1"
abort "unexpected scenario key" unless fixture.fetch("scenario_key") == "revocation"
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
expected_names = %w[route_after_confirmed_revocation reconnect_after_confirmed_revocation]
abort "fixture must cover revocation route and reconnect cases" unless cases.map { |example| example.fetch("name") }.sort == expected_names.sort

cases.each do |example|
  abort "revocation must be confirmed before rejection" unless example.fetch("pairing_revocation_confirmed") == true
  abort "case must attempt either route or handshake" unless example.fetch("route_attempted") ^ example.fetch("handshake_attempted")
  abort "revoked pairing must map to PAIRING_INVALID" unless example.fetch("expected_error") == "PAIRING_INVALID"
  abort "revoked pairing must not be routeable" unless example.fetch("route_allowed") == false
  abort "revoked pairing must not establish a session" unless example.fetch("session_established") == false
  abort "Connector must retain authority history" unless example.fetch("connector_authority_history_deleted") == false
  abort "Relay must not persist business payload" unless example.fetch("business_payload_persisted_by_relay") == false
end

puts "revocation_semantics=passed"
puts "cases=#{cases.length}"
puts "business_data=false"
