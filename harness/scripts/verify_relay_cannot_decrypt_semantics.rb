#!/usr/bin/env ruby
# frozen_string_literal: true

require "json"

fixture_path = ARGV.fetch(0, File.expand_path("../fixtures/relay_cannot_decrypt.json", __dir__))
fixture = JSON.parse(File.read(fixture_path))

abort "fixture_version must be 0.1" unless fixture.fetch("fixture_version") == "0.1"
abort "unexpected scenario key" unless fixture.fetch("scenario_key") == "relay_cannot_decrypt"
abort "fixture must not contain business data" unless fixture.fetch("contains_business_data") == false
abort "Relay must not hold private keys" unless fixture.fetch("relay_holds_private_keys") == false
abort "E2EE must terminate at endpoints" unless fixture.fetch("e2ee_terminated_at") == "endpoints"

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
expected_names = %w[routing_payload_is_ciphertext_only relay_persistence_surface full_compromise_yields_no_plaintext]
abort "fixture must cover the three blindness semantics exactly once" unless cases.map { |c| c.fetch("name") }.sort == expected_names.sort

by_name = cases.to_h { |c| [c.fetch("name"), c] }

routing = by_name.fetch("routing_payload_is_ciphertext_only")
abort "routed bytes must be ciphertext" unless routing.fetch("routed_bytes_are_ciphertext") == true
abort "Relay must not read plaintext" unless routing.fetch("relay_reads_plaintext") == false
abort "Relay must not decrypt payload" unless routing.fetch("relay_decrypts_payload") == false

surface = by_name.fetch("relay_persistence_surface")
abort "persistence surface must be exactly pairing metadata, public keys and audit metadata" unless surface.fetch("persists").sort == %w[audit_metadata pairing_metadata public_keys]
abort "business payload, private keys and plaintext must never persist" unless surface.fetch("never_persists").sort == %w[business_payload plaintext private_keys]
abort "Relay must not persist business payload" unless surface.fetch("business_payload_persisted_by_relay") == false

breach = by_name.fetch("full_compromise_yields_no_plaintext")
abort "breach assumption must be full host and database read access" unless breach.fetch("assumed_breach") == "full relay host and database read access"
abort "full compromise must not yield plaintext" unless breach.fetch("plaintext_recoverable") == false
abort "full compromise must not yield private keys" unless breach.fetch("private_keys_recoverable") == false

puts "relay_cannot_decrypt_semantics=passed"
puts "cases=#{cases.length}"
puts "business_data=false"
