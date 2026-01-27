using UnityEngine;

public class BackgroundGradientMove : MonoBehaviour
{
    public float speed = 0.2f;
    private Material mat;
    private Vector2 offset;

    void Start()
    {
        mat = GetComponent<Renderer>().material;
    }

    void Update()
    {
        offset.x += Time.deltaTime * speed;
        offset.y += Time.deltaTime * speed * 0.5f;
        mat.mainTextureOffset = offset;
    }
}

