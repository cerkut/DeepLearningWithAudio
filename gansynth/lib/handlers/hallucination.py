from __future__ import print_function
import sys
import os
import random
import struct
import sys
import math

from ..utils import read_msg

import numpy as np
import scipy.io.wavfile as wavfile

from magenta.models.gansynth.lib import generate_util as gu

import struct
from .. import communication_struct as gss


def synthesize(model, zs, pitches):
    z_arr = np.array(zs)
    return model.generate_samples_from_z(z_arr, pitches)

def slerp(p0, p1, t):
  #Spherical linear interpolation.
  omega = np.arccos(np.dot(
      np.squeeze(p0/np.linalg.norm(p0)), np.squeeze(p1/np.linalg.norm(p1))))
  so = np.sin(omega)
  return np.sin((1.0-t)*omega) / so * p0 + np.sin(t*omega)/so * p1

def lerp(v0, v1, t):
  return (1 - t) * v0 + t * v1

def get_envelope(t_trim_start=0.0, t_attack=0.010, t_sustain=0.5, t_release=0.3, sr=16000):
    """
        Creates an attack sustain release amplitude envelope.
        Modified version of GANSynth generator utils.
        Added option to trim sound from the start of the sample, 
        and made t_attack be counted into the total length of the envelope.


        sr = Sample Rate
    """
    i_trim_start = int(sr * t_trim_start)
    i_attack = int(sr * t_attack)
    i_sustain = int(sr * t_sustain)
    i_release = int(sr * t_release)
    i_tot = i_trim_start + i_attack + i_sustain + i_release
    if i_tot > MAX_NOTE_LENGTH * sr:
        raise ValueError('Cannot generate evelope longer than ' + str(MAX_NOTE_LENGTH) + 
                         '. Tried to generate len = ' + str(i_tot / sr))

    envelope = np.ones(i_tot)
    # Linear attack
    if i_trim_start > 0:
        envelope[:i_trim_start] = 0
    envelope[i_trim_start:i_trim_start+i_attack] = np.linspace(0.0, 1.0, i_attack)
    # Linear release
    envelope[i_trim_start+i_attack+i_sustain:i_tot] = np.linspace(1.0, 0.0, i_release)
    return envelope

MAX_NOTE_LENGTH = 3.0

def interpolate_notes(notes, pitches, steps, use_linear = False):
    result_notes = []
    result_pitches = []
    for i in xrange(0, len(notes) - 1):
        start_note = notes[i]
        start_pitch = pitches[i]
        end_note = notes[i + 1]
        end_pitch = pitches[i + 1]
        
        result_notes.append(start_note)
        result_pitches.append(start_pitch)

        for step in xrange(1, steps + 1):
            interp = step / float(steps)
            if use_linear:
                result_notes.append([lerp(note, end_note[i], interp) for (i, note) in enumerate(start_note)])
            else:
                result_notes.append(slerp(start_note, end_note, interp))
            result_pitches.append(math.floor(lerp(start_pitch, end_pitch, interp)))
    
    result_notes.append(notes[-1])
    result_pitches.append(result_pitches[-1])

    return (result_notes, result_pitches)

def combine_notes(audio_notes, 
        vel = 0.5,
        sustain = 0.5,
        attack = 0.5,
        release = 0.5,
        start_trim = 0.1,
        spacing = 0.5,
        sr=16000):
    """Combine audio from multiple notes into a single audio clip.
    Args:
    audio_notes: Array of audio [n_notes, audio_samples].
    sr: Integer, sample rate.
    Returns:
    audio_clip: Array of combined audio clip [audio_samples]
    """
    MAX_VELOCITY = 127.0
    n_notes = len(audio_notes)
    
    

    clip_length = spacing * (n_notes + 1) + MAX_NOTE_LENGTH
    audio_clip = np.zeros(int(clip_length) * sr)

    

    for i in range(n_notes):
        # Generate an amplitude envelope
        envelope = get_envelope(start_trim, attack, sustain, release)
        length = len(envelope)
        audio_note = audio_notes[i, :length] * envelope
        # Normalize
        audio_note /= audio_note.max()
        audio_note *= (vel / MAX_VELOCITY)
        # Add to clip buffer
        clip_start = int(spacing * i * sr)
        clip_end = clip_start + length
        audio_clip[clip_start:clip_end] += audio_note

    # Normalize
    audio_clip /= audio_clip.max()
    audio_clip /= 2.0
    return audio_clip


def handle_hallucinate(model, stdin, stdout):
    hallucinate_msg = read_msg(stdin, gss.hallucinate_struct.size)
    args = gss.from_hallucinate_msg(hallucinate_msg)
    note_count, interpolation_steps, spacing, start_trim, attack, sustain, release = args

    print("note_count = {} interpolation_steps = {}, spacing = {}s, start_trim = {}s, attack = {}s, sustain = {}s, release = {}s".format(*args), file=sys.stderr)

    initial_notes = model.generate_z(note_count)
    initial_piches = np.array([32] * len(initial_notes)) # np.floor(30 + np.random.rand(len(initial_notes)) * 30)
    final_notes, final_pitches = interpolate_notes(initial_notes, initial_piches, interpolation_steps)

    audios = synthesize(model, final_notes, final_pitches)
    final_audio = combine_notes(audios, spacing = spacing, start_trim = start_trim, attack = attack, sustain = sustain, release = release)

    # TODO: Remove!
    try:
        gu.save_wav(final_audio, "/Users/oskar.koli/Desktop/hallucination.wav") 
    except Exception:
        pass

    final_audio = final_audio.astype('float32')

    stdout.write(gss.to_tag_msg(gss.OUT_TAG_AUDIO))
    stdout.write(gss.to_audio_size_msg(final_audio.size * final_audio.itemsize))
    stdout.write(gss.to_audio_msg(final_audio))


handlers = {
    gss.IN_TAG_HALLUCINATE: handle_hallucinate
}