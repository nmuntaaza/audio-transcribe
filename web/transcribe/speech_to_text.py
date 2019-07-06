from operator import itemgetter
from google.cloud import speech
from google.cloud.speech import enums
from google.cloud.speech import types
from google.cloud import storage


def upload_to_bucket(blob_name, path_to_file, bucket_name):
    """ Upload data to a bucket"""

    # Explicitly use service account credentials by specifying the private key
    # file.
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.blob(blob_name)
    blob.upload_from_filename(path_to_file)

    return blob.public_url


def transcribe_audio(path):
    """
        Deskripsi: Function untuk melakukan transkripsi audio

        Parameter:
            path: String

        Output:
            response: array
    """
    client = speech.SpeechClient()
    audio = types.RecognitionAudio(uri=path)

    config = types.RecognitionConfig(
        encoding=enums.RecognitionConfig.AudioEncoding.LINEAR16,
        language_code='id',
        enable_word_time_offsets=True)

    operation = client.long_running_recognize(config, audio)

    response = operation.result(timeout=90)

    return response


def process_transcript(response, label_speaker):
    transcript = []
    for result in response.results:
        alternative = result.alternatives[0]
        for word_info in alternative.words:
            word = word_info.word
            start_time = word_info.start_time
            end_time = word_info.end_time

            start_time = start_time.seconds + start_time.nanos * 1e-9
            end_time = end_time.seconds + end_time.nanos * 1e-9

            word_dict = {
                "speaker": label_speaker,
                "word": word,
                "start_time": start_time,
                "end_time": end_time
            }

            transcript.append(word_dict)

    return transcript


def sort_transcript(transcript1, transcript2):
    transcript = transcript1
    transcript.extend(transcript2)

    sorted_transcript = sorted(transcript, key=itemgetter('start_time'), reverse=False)

    return sorted_transcript


def generate_dialogue(transcript):
    sentence = ''
    dialogue = []
    first = True
    pLabel = 0
    label = transcript[0]['speaker']
    start_time = transcript[0]['start_time']

    for i in transcript:
        if i['speaker'] == label:
            sentence += i['word'] + ' '
        else:
            transcript = {
                'timestamp': str(start_time),
                'label': label,
                'sentence': sentence
            }
            sentence = ''

            dialogue.append(transcript)

            sentence += i['word'] + ' '
            first = False
            label = i['speaker']
            start_time = i['start_time']

    transcript = {
        'timestamp': str(start_time),
        'label': label,
        'sentence': sentence
    }

    dialogue.append(transcript)

    return dialogue
