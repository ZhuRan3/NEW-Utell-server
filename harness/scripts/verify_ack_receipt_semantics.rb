#!/usr/bin/env ruby
# frozen_string_literal: true

require "json"

fixture_path = ARGV.fetch(0, File.expand_path("../fixtures/ack_vs_persistent_receipt.json", __dir__))
fixture = JSON.parse(File.read(fixture_path))

abort "fixture_version must be 0.1" unless fixture.fetch("fixture_version") == "0.1"
abort "unexpected scenario key" unless fixture.fetch("scenario_key") == "ack_vs_persistent_receipt"
abort "fixture must not contain business data" unless fixture.fetch("contains_business_data") == false

cases = fixture.fetch("cases")
abort "fixture must contain exactly two cases" unless cases.length == 2

cases.each do |example|
  relay_ack = example.fetch("relay_ack_observed")
  persistent_receipt = example.fetch("connector_persistent_receipt_observed")
  expected = example.fetch("expected_phone_state")
  forbidden = example.fetch("forbidden_phone_states")

  abort "Relay ACK must be observed in every case" unless relay_ack == true
  abort "Relay ACK semantics must remain route-layer-only" unless example.fetch("relay_ack_semantics") == "route_layer_observation_only"

  expected_state = persistent_receipt ? "RECEIVED" : "UNKNOWN_RESULT"
  abort "case #{example.fetch('name')} maps to #{expected.inspect}, expected #{expected_state.inspect}" unless expected == expected_state
  abort "case #{example.fetch('name')} forbids its expected state" if forbidden.include?(expected)
  abort "case #{example.fetch('name')} treats ACK as commit" if !persistent_receipt && expected != "UNKNOWN_RESULT"
end

puts "ack_receipt_semantics=passed"
puts "cases=#{cases.length}"
puts "business_data=false"
