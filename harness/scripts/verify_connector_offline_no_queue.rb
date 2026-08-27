#!/usr/bin/env ruby
# frozen_string_literal: true

require "json"

fixture_path = ARGV.fetch(0, File.expand_path("../fixtures/connector_offline_no_queue.json", __dir__))
fixture = JSON.parse(File.read(fixture_path))

abort "fixture_version must be 0.1" unless fixture.fetch("fixture_version") == "0.1"
abort "unexpected scenario key" unless fixture.fetch("scenario_key") == "connector_offline_no_queue"
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

cases.each do |example|
  abort "route must be attempted" unless example.fetch("route_attempted") == true
  abort "Relay must not create an offline business queue" unless example.fetch("offline_business_queue_created") == false
  abort "Relay must not persist business payload" unless example.fetch("business_payload_persisted_by_relay") == false

  expected_error = example.fetch("connector_online") ? nil : "ROUTE_NOT_DELIVERED"
  abort "case #{example.fetch('name')} has incorrect route error" unless example.fetch("expected_route_error") == expected_error
end

puts "connector_offline_no_queue=passed"
puts "cases=#{cases.length}"
puts "business_data=false"
