#!/bin/bash

# Store the base64 encoded message
encoded_message="dGhpc2lzYXNlY3JldA=="

# Decode the base64 message and save the result
decoded_message=$(echo "$encoded_message" | base64 -d)

echo "---------------------------------------------------------- Decoded message base64:"
echo "$decoded_message"

# Try base32 decoding
base32_decode=$(echo "$encoded_message" | base32 -d 2>/dev/null || echo "Failed")

echo "---------------------------------------------------------- Decoded message base 32:"
echo "$base32_decode"

# Try hex decoding
hex_decode=$(echo "$encoded_message" | xxd -r -p 2>/dev/null || echo "Failed")

echo "---------------------------------------------------------- Decoded message hex:"
echo "$hex_decode"

# Try a second base64 decoding (if it's double-encoded)
double_base64=$(echo "$encoded_message" | base64 -d | base64 -d 2>/dev/null || echo "Failed")

echo "---------------------------------------------------------- Decoded message double base64:"
echo "$double_base64"

