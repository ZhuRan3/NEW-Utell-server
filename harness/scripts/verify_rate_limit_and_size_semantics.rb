#!/usr/bin/env ruby
# frozen_string_literal: true

require "json"

fixture_path = ARGV.fetch(0, File.expand_path("../fixtures/rate_limit_and_size.json", __dir__))
fixture = JSON.parse(File.read(fixture_path))

abort "fixture_version must be 0.1" unless fixture.fetch("fixture_version") == "0.1"
abort "unexpected scenario key" unless fixture.fetch("scenario_key") == "rate_limit_and_size"
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

params = fixture.fetch("confirmed_params")
abort "global concurrency limit must be 100" unless params.fetch("global_concurrency_limit") == 100
abort "global rate limit must be 300 per 60s" unless params.fetch("global_rate_limit") == 300 && params.fetch("rate_window_seconds") == 60
abort "pairing rate limit must be 5 per 60s" unless params.fetch("pairing_rate_limit") == 5 && params.fetch("pairing_window_seconds") == 60
abort "limit error code must be RATE_LIMITED" unless params.fetch("limit_error_code") == "RATE_LIMITED"
abort "message size cap must remain explicitly unfrozen" unless params.fetch("message_size_cap_frozen") == false

cases = fixture.fetch("cases")
abort "fixture must contain exactly five cases" unless cases.length == 5
expected_names = %w[global_concurrency_gate_exact global_rate_gate_exact pairing_rate_gate_exact pairing_rate_independence message_size_not_frozen]
abort "fixture must cover the five gates exactly once" unless cases.map { |c| c.fetch("name") }.sort == expected_names.sort

by_name = cases.to_h { |c| [c.fetch("name"), c] }

conc = by_name.fetch("global_concurrency_gate_exact")
abort "concurrency gate must accept exactly the limit" unless conc.fetch("accepted") == params.fetch("global_concurrency_limit")
abort "concurrency gate arithmetic mismatch" unless conc.fetch("accepted") + conc.fetch("rate_limited") == conc.fetch("attempts")
abort "concurrency gate must not produce other failures" unless conc.fetch("other_failures") == 0
abort "concurrency gate must map rejections to RATE_LIMITED" unless conc.fetch("error_code") == "RATE_LIMITED"

rate = by_name.fetch("global_rate_gate_exact")
abort "rate gate must accept exactly the limit" unless rate.fetch("accepted") == params.fetch("global_rate_limit")
abort "rate gate arithmetic mismatch" unless rate.fetch("accepted") + rate.fetch("rate_limited") == rate.fetch("attempts")
abort "rate gate must not produce other failures" unless rate.fetch("other_failures") == 0
abort "rate gate must map rejections to RATE_LIMITED" unless rate.fetch("error_code") == "RATE_LIMITED"

pair = by_name.fetch("pairing_rate_gate_exact")
abort "pairing gate must accept exactly the pairing limit" unless pair.fetch("accepted") == params.fetch("pairing_rate_limit")
abort "pairing gate arithmetic mismatch" unless pair.fetch("accepted") + pair.fetch("rate_limited") == pair.fetch("same_pairing_attempts_in_window")
abort "pairing gate must map rejections to RATE_LIMITED" unless pair.fetch("error_code") == "RATE_LIMITED"
abort "pairing gate must be independent of the global layer" unless pair.fetch("independent_of_global_layer") == true

fan = by_name.fetch("pairing_rate_independence")
abort "distinct pairings must all be admitted" unless fan.fetch("accepted") == fan.fetch("distinct_pairings") * fan.fetch("attempts_per_pairing")
abort "distinct pairings must not be pairing-limited" unless fan.fetch("rate_limited") == 0 && fan.fetch("other_failures") == 0

size = by_name.fetch("message_size_not_frozen")
abort "size cap must not be defined before G3 freeze" unless size.fetch("size_cap_defined") == false
abort "Relay must never persist payload regardless of size" unless size.fetch("relay_persists_payload") == false

puts "rate_limit_and_size_semantics=passed"
puts "cases=#{cases.length}"
puts "business_data=false"
