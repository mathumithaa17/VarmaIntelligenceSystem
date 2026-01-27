using System;

[Serializable]
public class VarmaData
{
    public string varmaName;
    public string signs;
    public string pathognomicSign;
    public string indications;
    public string tamilLiterature;
}

[Serializable]
public class VarmaDataWrapper
{
    public VarmaData[] varmas;
}

