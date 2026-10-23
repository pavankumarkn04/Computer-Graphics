
using UnityEngine;

public class InteractiveScene : MonoBehaviour
{
    GameObject ground, cube, sphere, cylinder;
    GameObject selected;

    Vector3 startPosition, startScale;
    Quaternion startRotation;

    float moveSpeed = 3f;
    float rotateSpeed = 90f;
    float scaleSpeed = 1f;

    void Start()
    {
        // Remove previously generated objects
        GameObject old = GameObject.Find("Ground");
        if (old != null) Destroy(old);

        old = GameObject.Find("Cube");
        if (old != null) Destroy(old);

        old = GameObject.Find("Sphere");
        if (old != null) Destroy(old);

        old = GameObject.Find("Cylinder");
        if (old != null) Destroy(old);

        // Create one large ground
        ground = GameObject.CreatePrimitive(PrimitiveType.Plane);
        ground.name = "Ground";
        ground.transform.position = new Vector3(0, 0, 0);
        ground.transform.localScale = new Vector3(100, 1, 100);
        SetColor(ground, new Color(0.15f, 0.55f, 0.2f));

        // Create cube
        cube = GameObject.CreatePrimitive(PrimitiveType.Cube);
        cube.name = "Cube";
        cube.transform.position = new Vector3(0, 1, 0);
        SetColor(cube, Color.cyan);

        // Create sphere
        sphere = GameObject.CreatePrimitive(PrimitiveType.Sphere);
        sphere.name = "Sphere";
        sphere.transform.position = new Vector3(-2, 1, 0);
        SetColor(sphere, Color.yellow);

        // Create cylinder
        cylinder = GameObject.CreatePrimitive(PrimitiveType.Cylinder);
        cylinder.name = "Cylinder";
        cylinder.transform.position = new Vector3(2, 1, 0);
        SetColor(cylinder, Color.red);

        // Camera setup
        Camera cam = Camera.main;

        if (cam != null)
        {
            cam.transform.position = new Vector3(0, 8, -12);
            cam.transform.LookAt(new Vector3(0, 1, 0));
            cam.clearFlags = CameraClearFlags.SolidColor;
            cam.backgroundColor = new Color(0.15f, 0.2f, 0.3f);
        }

        SelectObject(cube);
    }

    void Update()
    {
        if (Input.GetKeyDown(KeyCode.Alpha1))
            SelectObject(cube);

        if (Input.GetKeyDown(KeyCode.Alpha2))
            SelectObject(sphere);

        if (Input.GetKeyDown(KeyCode.Alpha3))
            SelectObject(cylinder);

        if (selected == null) return;

        // Translation
        float x = Input.GetAxis("Horizontal");
        float z = Input.GetAxis("Vertical");

        selected.transform.Translate(
            new Vector3(x, 0, z) * moveSpeed * Time.deltaTime,
            Space.World
        );

        // Rotation
        if (Input.GetKey(KeyCode.Q))
            selected.transform.Rotate(
                Vector3.up, -rotateSpeed * Time.deltaTime);

        if (Input.GetKey(KeyCode.E))
            selected.transform.Rotate(
                Vector3.up, rotateSpeed * Time.deltaTime);

        // Scaling
        if (Input.GetKey(KeyCode.Equals) ||
            Input.GetKey(KeyCode.KeypadPlus))
        {
            selected.transform.localScale +=
                Vector3.one * scaleSpeed * Time.deltaTime;
        }

        if (Input.GetKey(KeyCode.Minus) ||
            Input.GetKey(KeyCode.KeypadMinus))
        {
            Vector3 s = selected.transform.localScale -
                Vector3.one * scaleSpeed * Time.deltaTime;

            selected.transform.localScale = new Vector3(
                Mathf.Max(0.2f, s.x),
                Mathf.Max(0.2f, s.y),
                Mathf.Max(0.2f, s.z)
            );
        }

        // Reset
        if (Input.GetKeyDown(KeyCode.R))
        {
            selected.transform.position = startPosition;
            selected.transform.rotation = startRotation;
            selected.transform.localScale = startScale;
        }
    }

    void SelectObject(GameObject obj)
    {
        selected = obj;
        startPosition = obj.transform.position;
        startRotation = obj.transform.rotation;
        startScale = obj.transform.localScale;

        Debug.Log("Selected: " + obj.name);
    }

    void SetColor(GameObject obj, Color color)
    {
        obj.GetComponent<Renderer>().material.color = color;
    }
}
