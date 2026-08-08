#!/bin/bash
# ReSpeaker 2-Mics HAT v2 - Audio setup script
# Sets playback, speaker, and mic levels on card seeed2micvoicec

CARD="seeed2micvoicec"

echo "==> Configuring ReSpeaker 2-Mics HAT audio levels..."

# --- PLAYBACK OUTPUT (headphone + JST amp input) ---
amixer -c $CARD sset 'PCM' 255,255          # DAC digital volume - max
amixer -c $CARD sset 'Speaker' 127,127      # Speaker amp output - max
amixer -c $CARD sset 'Headphone' 127,127    # Headphone output

# --- MAKE SURE OUTPUT IS UNMUTED ---
amixer -c $CARD sset 'Speaker' unmute
amixer -c $CARD sset 'Headphone' unmute

# --- MIC / CAPTURE INPUT ---
amixer -c $CARD sset 'Capture' 63,63        # ADC capture level
amixer -c $CARD sset 'Capture' cap          # Enable capture

# --- ALC (Auto Level Control) - disable for cleaner mic input ---
amixer -c $CARD sset 'ALC Function' 'Off' 2>/dev/null || true

echo "==> Done! Saving state..."
sudo alsactl store

echo ""
echo "==> Current mixer state:"
amixer -c $CARD
