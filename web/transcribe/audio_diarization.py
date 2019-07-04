from pyAudioAnalysis import audioSegmentation as aS


def audio_diarization(audio, sr, number_of_speaker, verbose=False):
    
    time = 0.0
    first_time = 0.0
    nol = []
    one = []
    speaker_speech = []
    
    diarization = aS.speakerDiarization(audio, sr, number_of_speaker, plot_res=False)
    # Mengambil Label pada 0.2 detik pertama
    first = diarization[0]
    
    if verbose:
        print("Speaker: {}, len : {}".format(diarization,len(diarization)))

    for index, i in enumerate(diarization):
        if i == first and index < (len(diarization))-1:
            time += 0.2
        else:
            audio_clip = audio[int(sr*first_time):int(sr*time)]

            if int(i) < 1:
                # Jika Label Speaker 0
                nol[int(sr*first_time):int(sr*time)] = audio_clip
                one[int(sr*first_time):int(sr*time)] = [0 for k in range(int(sr*time) - int(sr*first_time))]
            else:
                # Jika Label Speaker 1
                one[int(sr*first_time):int(sr*time)] = audio_clip
                nol[int(sr*first_time):int(sr*time)] = [0 for k in range(int(sr*time) - int(sr*first_time))]
                
            if verbose:
                print("Speaker: {}".format(first))
                print("Timestamp: {}-{}".format(first_time, time))
                print("")    
            
            first_time = time
            first = i
            last_speaker = i

    # Proses Pemisahan Label Terakhir
    audio_clip = audio[int(sr*first_time):int(sr*time)]
    
    if int(last_speaker) < 1:
        nol[int(sr*first_time):int(sr*time)] = audio_clip
        one[int(sr*first_time):int(sr*time)] = [0 for k in range(int(sr*time) - int(sr*first_time))]
    else:
        one[int(sr*first_time):int(sr*time)] = audio_clip
        nol[int(sr*first_time):int(sr*time)] = [0 for k in range(int(sr*time) - int(sr*first_time))]
        
    speaker_speech.append(nol)
    speaker_speech.append(one)
    
    return speaker_speech
