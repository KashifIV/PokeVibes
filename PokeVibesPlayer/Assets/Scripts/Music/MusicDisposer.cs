using System.Collections.Generic;
using System;
using System.IO;
using System.Linq;

public class MusicDisposer {
    private string _favouritePath, _lPath;
    public MusicDisposer(string dataPath)
    {
        string path = GetRootPath(dataPath);
        _favouritePath = Path.Join(path, "favourites");
        _lPath = Path.Join(path, "learning");
    }

    public void Dispose(AudioSample sample)
    {
        
    }
    private string GetRootPath(string dataPath)
    {
        List<string> parts = dataPath.Split("/").ToList();
        int index = parts.FindIndex(x => x == "PokeVibesPlayer");
        parts = parts.GetRange(0, index);
        return String.Join("/", parts) + "/";
    }
}
