
using UnityEngine;

public class ProjectionLab : MonoBehaviour
{
    GameObject root;
    GameObject[] objects = new GameObject[4];
    Vector3[] startPos = new Vector3[4];
    Vector3[] startScale = new Vector3[4];
    Quaternion[] startRot = new Quaternion[4];

    Camera cam;
    int selected = 0;

    bool perspective = true;
    bool autoRotate = true;
    bool inset = false;

    float angle = 0f;
    float zoom = 10f;
    float height = 5f;

    void Start()
    {
        // Remove old generated groups
        GameObject[] all =
            FindObjectsByType<GameObject>(FindObjectsSortMode.None);

        foreach (GameObject go in all)
        {
            if (go != gameObject &&
                go.name == "Projection Lab Objects")
            {
                Destroy(go);
            }
        }

        // Create one clean group
        root = new GameObject("Projection Lab Objects");

        // Ground
        CreateObject(PrimitiveType.Plane, "Ground",
            new Vector3(0, 0, 0),
            new Vector3(5, 1, 5),
            new Color(0.12f, 0.16f, 0.23f));

        // Objects
        objects[0] = CreateObject(PrimitiveType.Cube, "Cyan Cube",
            new Vector3(-2, 0.8f, 0), Vector3.one * 1.6f,
            Color.cyan);

        objects[1] = CreateObject(PrimitiveType.Sphere, "Yellow Sphere",
            new Vector3(0, 0.8f, 0), Vector3.one * 1.6f,
            Color.yellow);

        objects[2] = CreateObject(PrimitiveType.Cylinder, "Red Cylinder",
            new Vector3(2, 1, 0), Vector3.one * 1.5f,
            Color.red);

        objects[3] = CreateObject(PrimitiveType.Capsule, "Green Capsule",
            new Vector3(0, 0.9f, 2), Vector3.one * 1.5f,
            Color.green);

        for (int i = 0; i < objects.Length; i++)
        {
            startPos[i] = objects[i].transform.position;
            startScale[i] = objects[i].transform.localScale;
            startRot[i] = objects[i].transform.rotation;
        }

        // Camera
        cam = Camera.main;

        if (cam == null)
        {
            GameObject cameraObj = new GameObject("Main Camera");
            cam = cameraObj.AddComponent<Camera>();
            cameraObj.tag = "MainCamera";
        }

        cam.rect = new Rect(0, 0, 1, 1);
        cam.clearFlags = CameraClearFlags.SolidColor;
        cam.backgroundColor = new Color(0.04f, 0.06f, 0.12f);
        cam.fieldOfView = 60f;
        cam.nearClipPlane = 0.1f;
        cam.farClipPlane = 200f;

        // Lighting
        Light light = FindFirstObjectByType<Light>();

        if (light == null)
        {
            GameObject lightObj = new GameObject("Scene Light");
            light = lightObj.AddComponent<Light>();
            light.type = LightType.Directional;
        }

        light.intensity = 1.5f;
        light.transform.rotation = Quaternion.Euler(45, -30, 0);

        UpdateCamera();
    }

    GameObject CreateObject(
        PrimitiveType type, string objName,
        Vector3 pos, Vector3 scale, Color color)
    {
        GameObject obj = GameObject.CreatePrimitive(type);
        obj.name = objName;
        obj.transform.SetParent(root.transform);
        obj.transform.position = pos;
        obj.transform.localScale = scale;

        Renderer rend = obj.GetComponent<Renderer>();
        Shader shader = Shader.Find("Universal Render Pipeline/Lit");

        if (shader == null)
            shader = Shader.Find("Standard");

        if (shader != null)
        {
            Material mat = new Material(shader);
            mat.color = color;
            rend.material = mat;
        }

        return obj;
    }

    void Update()
    {
        if (cam == null || objects[0] == null) return;

        // Select objects
        if (Input.GetKeyDown(KeyCode.Alpha1)) selected = 0;
        if (Input.GetKeyDown(KeyCode.Alpha2)) selected = 1;
        if (Input.GetKeyDown(KeyCode.Alpha3)) selected = 2;
        if (Input.GetKeyDown(KeyCode.Alpha4)) selected = 3;

        // Projection
        if (Input.GetKeyDown(KeyCode.P))
            perspective = !perspective;

        // Viewport mapping demonstration
        if (Input.GetKeyDown(KeyCode.V))
            inset = !inset;

        if (Input.GetKeyDown(KeyCode.Space))
            autoRotate = !autoRotate;

        // Camera orbit
        if (Input.GetKey(KeyCode.LeftArrow)) angle -= 50 * Time.deltaTime;
        if (Input.GetKey(KeyCode.RightArrow)) angle += 50 * Time.deltaTime;

        if (Input.GetKey(KeyCode.UpArrow))
            height = Mathf.Min(9, height + 3 * Time.deltaTime);

        if (Input.GetKey(KeyCode.DownArrow))
            height = Mathf.Max(2, height - 3 * Time.deltaTime);

        if (Input.GetKey(KeyCode.Equals) ||
            Input.GetKey(KeyCode.KeypadPlus))
            zoom = Mathf.Max(4, zoom - 5 * Time.deltaTime);

        if (Input.GetKey(KeyCode.Minus) ||
            Input.GetKey(KeyCode.KeypadMinus))
            zoom = Mathf.Min(18, zoom + 5 * Time.deltaTime);

        GameObject obj = objects[selected];

        // Object movement
        float x = Input.GetAxis("Horizontal");
        float z = Input.GetAxis("Vertical");

        obj.transform.Translate(
            new Vector3(x, 0, z) * 3f * Time.deltaTime,
            Space.World);

        if (Input.GetKey(KeyCode.Q))
            obj.transform.Rotate(Vector3.up, -90 * Time.deltaTime);

        if (Input.GetKey(KeyCode.E))
            obj.transform.Rotate(Vector3.up, 90 * Time.deltaTime);

        if (autoRotate)
            obj.transform.Rotate(Vector3.up, 20 * Time.deltaTime);

        // Reset selected object
        if (Input.GetKeyDown(KeyCode.R))
        {
            obj.transform.position = startPos[selected];
            obj.transform.localScale = startScale[selected];
            obj.transform.rotation = startRot[selected];
        }

        UpdateCamera();
    }

    void UpdateCamera()
    {
        if (cam == null) return;

        cam.orthographic = !perspective;

        if (!perspective)
            cam.orthographicSize = zoom * 0.55f;

        Vector3 target = new Vector3(0, 0.8f, 0);

        float rad = angle * Mathf.Deg2Rad;

        Vector3 offset = new Vector3(
            Mathf.Sin(rad) * zoom,
            height,
            -Mathf.Cos(rad) * zoom);

        cam.transform.position = target + offset;
        cam.transform.LookAt(target);

        cam.rect = inset
            ? new Rect(0.60f, 0.05f, 0.37f, 0.37f)
            : new Rect(0, 0, 1, 1);
    }

    void OnGUI()
    {
        GUI.Box(new Rect(12, 12, 300, 270),
            "3D VIEWING PIPELINE");

        GUI.Label(new Rect(25, 42, 280, 22),
            "Projection: " +
            (perspective ? "Perspective" : "Orthographic"));

        GUI.Label(new Rect(25, 65, 280, 22),
            "Selected: " + objects[selected].name);

        GUI.Label(new Rect(25, 95, 280, 22),
            "1-4 : Select object");

        GUI.Label(new Rect(25, 118, 280, 22),
            "WASD : Move object");

        GUI.Label(new Rect(25, 141, 280, 22),
            "Q / E : Rotate object");

        GUI.Label(new Rect(25, 164, 280, 22),
            "Arrow keys : Move camera view");

        GUI.Label(new Rect(25, 187, 280, 22),
            "+ / - : Zoom");

        GUI.Label(new Rect(25, 210, 280, 22),
            "P : Projection | V : Viewport");

        GUI.Label(new Rect(25, 233, 280, 22),
            "Space : Auto rotate");

        GUI.Label(new Rect(25, 252, 280, 22),
            "R : Reset selected object");
    }
}
