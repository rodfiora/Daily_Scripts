#!/usr/bin/env bash

BITS=24
MAX=$(( (1 << BITS) - 1 ))

read -p "Decimal value (0 to $MAX): " value

# Ensure value is within 24 bits
value=$(( value & MAX ))

echo
echo "24-bit binary representation:"
echo "23 22 21 20  19 18 17 16  15 14 13 12  11 10  9  8   7  6  5  4   3  2  1  0"

binary=""
for (( i=BITS-1; i>=0; i-- )); do
    bit=$(( (value >> i) & 1 ))
    binary+=" $bit "

    # Optional spacing every 4 bits
    if (( i % 4 == 0 && i != 0 )); then
        binary+=" "
    fi
done

echo "$binary"
echo
echo "Bit positions = 1:"

for (( i=0; i<BITS; i++ )); do
    if (( (value >> i) & 1 )); then
        echo "Bit $i"
    fi
done
