using UnityEngine;

public class HumanRotate : MonoBehaviour
{
    public float rotationSpeed = 100f;
    [HideInInspector] public bool allowRotation = true;

    void Update()
    {
        if (!allowRotation)
        {
            Debug.Log("HumanRotate: rotation locked");
            return;
        }

        if (Input.GetMouseButton(0))
        {
            float mouseX = Input.GetAxis("Mouse X");
            transform.Rotate(Vector3.up, -mouseX * rotationSpeed * Time.deltaTime, Space.World);
            Debug.Log("HumanRotate: rotating");
        }
    }
}
