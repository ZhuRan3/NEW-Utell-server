#!/usr/bin/env ruby
# frozen_string_literal: true

require "json"

fixture_path = ARGV.fetch(0, File.expand_path("../fixtures/relay_restart.json", __dir__))
fixture = JSON.parse(File.read(fixture_path))

abort "fixture_version must be 0.1" unless fixture.fetch("fixture_version") == "0.1"
abort "unexpected scenario key" unless fixture.fetch("scenario_key") == "relay_restart"
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
abort "fixture must contain exactly four cases" unless cases.length == 4
expected_names = %w[restart_preserves_registry restart_drops_inflight_ciphertext restart_requires_new_session health_endpoint_recovers]
abort "fixture must cover the four restart semantics exactly once" unless cases.map { |c| c.fetch("name") }.sort == expected_names.sort

by_name = cases.to_h { |c| [c.fetch("name"), c] }

registry = by_name.fetch("restart_preserves_registry")
abort "pairing registry must survive restart" unless registry.fetch("pairing_registry_preserved") == true
abort "public keys must survive restart" unless registry.fetch("public_keys_preserved") == true
abort "audit metadata must survive restart" unless registry.fetch("audit_metadata_preserved") == true
abort "audit retention must be 14 days" unless registry.fetch("audit_retention_days") == 14

inflight = by_name.fetch("restart_drops_inflight_ciphertext")
abort "in-flight undelivered ciphertext must not be recovered" unless inflight.fetch("inflight_undelivered_recovered") == false
abort "restart must not create an offline queue" unless inflight.fetch("offline_queue_created") == false
abort "Relay must not persist business payload" unless inflight.fetch("business_payload_persisted_by_relay") == false
abort "sender must observe RELAY_UNREACHABLE during restart" unless inflight.fetch("sender_observes") == "RELAY_UNREACHABLE"

session = by_name.fetch("restart_requires_new_session")
abort "old sessions must not be resumed" unless session.fetch("old_sessions_resumed") == false
abort "full handshake must be required after restart" unless session.fetch("full_handshake_required") == true
abort "all reconnect attempts must succeed" unless session.fetch("reconnect_succeeded") == session.fetch("reconnect_attempts")

health = by_name.fetch("health_endpoint_recovers")
abort "healthz must return 204 after restart" unless health.fetch("healthz_status_after_restart") == 204
abort "health report interval must be 10 seconds" unless health.fetch("health_report_interval_seconds") == 10

puts "relay_restart_semantics=passed"
puts "cases=#{cases.length}"
puts "business_data=false"
