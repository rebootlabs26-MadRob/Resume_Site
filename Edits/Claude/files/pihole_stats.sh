#!/bin/bash
STATS=$(curl -s http://MadGuard/admin/api.php)
TOTAL=$(echo "$STATS" | grep -o '"dns_queries_today":[0-9]*' | cut -d: -f2)
BLOCKED=$(echo "$STATS" | grep -o '"ads_blocked_today":[0-9]*' | cut -d: -f2)
PERCENT=$(echo "$STATS" | grep -o '"ads_percentage_today":[0-9.]*' | cut -d: -f2)
CACHED=$(echo "$STATS" | grep -o '"queries_cached":[0-9]*' | cut -d: -f2)
FORWARDED=$(echo "$STATS" | grep -o '"queries_forwarded":[0-9]*' | cut -d: -f2)
DOMAINS=$(echo "$STATS" | grep -o '"unique_domains":[0-9]*' | cut -d: -f2)

echo "{\"queries_total\":$TOTAL,\"queries_blocked\":$BLOCKED,\"percent_blocked\":$PERCENT,\"queries_cached\":$CACHED,\"queries_forwarded\":$FORWARDED,\"unique_domains\":$DOMAINS}"
