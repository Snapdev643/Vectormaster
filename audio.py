import pygame as pg
import numpy as np
import time

# Initialize pygame mixer with high quality settings
pg.mixer.init(frequency=44100, size=-16, channels=2)  # Changed to 2 channels for stereo

class Audio:
    def __init__(self):
        self.sample_rate = 44100
        self.amplitude = 32767  # Maximum amplitude for 16-bit audio
        self.wave_length = 16   # Length of each waveform pattern
        
        # 17 pre-defined waveform patterns (values from 0 to 16)
        self.waves = {
            '0': [8, 5, 2, 1, 0, 1, 2, 5, 8, 10, 13, 14, 15, 14, 13, 10],  # sine
            '1': [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15],   # sawtooth
            '2': [0, 2, 4, 6, 8, 10, 12, 14, 15, 14, 12, 10, 8, 6, 4, 2],  # triangle
            '3': [0, 0, 0, 0, 0, 0, 0, 0, 15, 15, 15, 15, 15, 15, 15, 15], # square 50%
            '4': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 15, 15, 15, 15], #Square 25%
            '5': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 15, 15], #Square 12%
            '6': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 15], #Square 6%
            '7': [8, 5, 2, 1, 0, 1, 2, 5, 8, 10, 9, 12, 15, 12, 9, 10], #distorted sine
            '8': [7, 9, 10, 11, 10, 9, 7, 5, 8, 10, 13, 14, 11, 12, 14, 15], #square-sine
            '9': [7, 12, 14, 12, 7, 2, 0, 2, 7, 13, 13, 7, 1, 1, 7, 7], #bass
            '10': [7, 13, 13, 10, 13, 15, 10, 6, 7, 9, 4, 0, 1, 4, 1, 1], #organ1
            '11': [7, 15, 13, 9, 11, 10, 6, 3, 7, 11, 8, 4, 3, 5, 1, 0], #organ2
            '12': [0, 15, 1, 14, 2, 13, 3, 12, 4, 11, 5, 10, 6, 9, 7, 8], #harmonics1
            '13': [8, 5, 10, 3, 11, 1, 13, 0, 15, 1, 13, 3, 11, 5, 6, 6], #harmonics 2
            '14': [0, 0, 0, 2, 8, 14, 4, 10, 0, 6, 12, 2, 8, 14, 15, 15], #guitar1
            '15': [0, 15, 0, 15, 0, 15, 15, 0, 15, 15, 15, 15, 15, 15, 15, 15], #guitar2
            '16': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], #Noise
        }

        # Pre-generate normalized wave tables for faster lookup
        self.wave_tables = {}
        for wave_idx, pattern in self.waves.items():
            wave_array = np.array(pattern, dtype=np.float32)
            wave_array = ((wave_array / 7.5) - 1.0) * self.amplitude
            self.wave_tables[wave_idx] = wave_array

        # Channel state: [wave_index, volume (0-15), frequency, is_playing]
        self.channels = [[0, 0, 440.0, False], [0, 0, 440.0, False]]
        
        # Sound buffer length (1/60th of a second for 60fps)
        self.buffer_samples = self.sample_rate // 60

        # Cache for frequency-specific sample arrays
        self.sample_cache = {}
        
    def set_channel(self, channel, wave_index, volume, frequency):
        """Set channel parameters"""
        if 0 <= channel < len(self.channels):
            self.channels[channel] = [wave_index, min(15, max(0, volume)), frequency, True]
    
    def stop_channel(self, channel):
        """Stop playback on a channel"""
        if 0 <= channel < len(self.channels):
            self.channels[channel][3] = False
    
    def generate_samples(self, num_samples):
        """Generate audio samples for all active channels"""
        # Initialize output buffer (stereo)
        output = np.zeros((num_samples, 2), dtype=np.float32)
        
        # Process each channel
        for channel_idx, (wave_idx, volume, frequency, is_playing) in enumerate(self.channels):
            if not is_playing or volume == 0:
                continue

            # Use cached samples if available for this frequency and wave
            cache_key = (str(wave_idx), frequency)
            if cache_key in self.sample_cache and str(wave_idx) != '16':  # Don't cache noise
                channel_samples = self.sample_cache[cache_key][:num_samples]
            else:
                # Calculate samples per cycle
                samples_per_cycle = self.sample_rate / frequency
                
                # Generate time points
                t = np.arange(num_samples)
                
                if str(wave_idx) == '16':  # Noise channel
                    # Generate fresh noise samples with frequency-based filtering
                    noise = np.random.uniform(-self.amplitude, self.amplitude, num_samples)
                    if frequency <= 8:  # Use frequency as a noise color parameter (1-8)
                        # Apply simple low-pass filter based on frequency
                        # Lower frequency = more filtering
                        filter_size = int((9 - frequency) * 8)  # More filtering for lower frequencies
                        if filter_size > 1:
                            kernel = np.ones(filter_size) / filter_size
                            noise = np.convolve(noise, kernel, mode='same')
                    channel_samples = noise
                else:
                    # Get pre-normalized wave table
                    wave_table = self.wave_tables.get(str(wave_idx), self.wave_tables['0'])
                    
                    # Calculate indices into the wave pattern
                    pattern_indices = ((t * frequency / self.sample_rate * self.wave_length) % self.wave_length).astype(int)
                    
                    # Get samples from wave pattern
                    channel_samples = wave_table[pattern_indices]

                    # Cache the generated samples (except noise)
                    if str(wave_idx) != '16':
                        self.sample_cache[cache_key] = channel_samples.copy()
            
            # Apply volume scaling
            channel_samples = channel_samples * (volume / 15.0)
            
            # Add to both left and right channels
            output[:, 0] += channel_samples  # Left channel
            output[:, 1] += channel_samples  # Right channel
        
        # Clear cache if it gets too large
        if len(self.sample_cache) > 1000:
            self.sample_cache.clear()

        # Normalize and convert to 16-bit integers
        output = np.clip(output, -self.amplitude, self.amplitude)
        return output.astype(np.int16)
    
    def update(self):
        """Generate and queue the next buffer of audio"""
        if any(channel[3] for channel in self.channels):  # If any channel is playing
            samples = self.generate_samples(self.buffer_samples)
            sound = pg.sndarray.make_sound(samples)
            pg.mixer.find_channel(True).play(sound)
    
    def play_tone(self, channel, wave_index, volume, frequency, duration=None):
        """Play a tone on a channel with optional duration"""
        self.set_channel(channel, wave_index, volume, frequency)
        
        if duration is not None:
            start_time = time.time()
            end_time = start_time + duration
            
            # Keep updating audio until duration is reached
            while time.time() < end_time:
                self.update()
                pg.time.wait(1)  # Small delay to prevent CPU overload
            
            self.stop_channel(channel)

    