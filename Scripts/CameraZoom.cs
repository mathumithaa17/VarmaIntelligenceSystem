using UnityEngine;

public class CameraOrbitPanZoom : MonoBehaviour
{
    [Header("Target")]
    public Transform defaultTarget; // HUMAN root

    [Header("Zoom")]
    public float zoomSpeed = 6f;
    public float minDistance = 0.8f;
    public float maxDistance = 15f;
    public float zoomSmoothTime = 0.12f;

    [Header("Rotation")]
    public float rotateSpeed = 3f;

    [Header("Pan")]
    public float panSpeed = 0.015f;
    public float keyboardPanSpeed = 2.5f;

    private Vector3 focusPoint;
    private float currentDistance;
    private float targetDistance;
    private float zoomVelocity;

    private float yaw;
    private float pitch;

    void Start()
    {
        if (!defaultTarget)
        {
            Debug.LogError("Default target (HUMAN) not assigned!");
            enabled = false;
            return;
        }

        focusPoint = defaultTarget.position;

        currentDistance = Vector3.Distance(transform.position, focusPoint);
        targetDistance = currentDistance;

        Vector3 angles = transform.eulerAngles;
        yaw = angles.y;
        pitch = angles.x;

        // 🔒 Prevent clipping issues
        Camera cam = GetComponent<Camera>();
        if (cam) cam.nearClipPlane = 0.01f;
    }

    void LateUpdate()
    {
        HandleZoom();
        HandleRotation();
        HandlePan();
        UpdateCamera();
    }

    // ✅ CALLED FROM VarmaClickManager
    public void SetFocusPoint(Vector3 point)
    {
        focusPoint = point;

        // 🔑 CRITICAL FIX
        currentDistance = Mathf.Clamp(
            Vector3.Distance(transform.position, focusPoint),
            minDistance,
            maxDistance
        );

        targetDistance = currentDistance;
    }

    void HandleZoom()
    {
        float scroll = Input.GetAxis("Mouse ScrollWheel");

        if (Mathf.Abs(scroll) > 0.001f)
        {
            targetDistance -= scroll * zoomSpeed;
            targetDistance = Mathf.Clamp(targetDistance, minDistance, maxDistance);
        }

        currentDistance = Mathf.SmoothDamp(
            currentDistance,
            targetDistance,
            ref zoomVelocity,
            zoomSmoothTime
        );
    }

    void HandleRotation()
    {
        if (Input.GetMouseButton(0)) // Left click drag
        {
            yaw += Input.GetAxis("Mouse X") * rotateSpeed * 120f * Time.deltaTime;
            pitch -= Input.GetAxis("Mouse Y") * rotateSpeed * 120f * Time.deltaTime;
            pitch = Mathf.Clamp(pitch, -85f, 85f);
        }
    }

    void HandlePan()
    {
        // ⌨️ Keyboard pan (WASD / Arrow keys)
        float h = Input.GetAxis("Horizontal");
        float v = Input.GetAxis("Vertical");

        if (Mathf.Abs(h) > 0.01f || Mathf.Abs(v) > 0.01f)
        {
            focusPoint += (transform.right * h + transform.up * v)
                          * keyboardPanSpeed * Time.deltaTime;
        }

        // 🖱️ Mouse pan (Right click drag)
        if (Input.GetMouseButton(1))
        {
            float mx = -Input.GetAxis("Mouse X");
            float my = -Input.GetAxis("Mouse Y");

            focusPoint += (transform.right * mx + transform.up * my)
                          * panSpeed * currentDistance;
        }
    }

    void UpdateCamera()
    {
        Quaternion rotation = Quaternion.Euler(pitch, yaw, 0f);
        Vector3 direction = rotation * Vector3.forward;

        transform.position = focusPoint - direction * currentDistance;
        transform.rotation = rotation;
    }
}
