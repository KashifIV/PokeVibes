using UnityEngine;

public struct AudioSample {
    public string Path { get; private set; }
    public AudioClip AudioClip { get; private set; }

    public AudioSample(string path, AudioClip audioClip)
    {
        this.Path = path;
        this.AudioClip = audioClip;
    }
}
