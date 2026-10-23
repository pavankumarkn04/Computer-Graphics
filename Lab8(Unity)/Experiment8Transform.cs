using UnityEngine;

[RequireComponent(typeof(MeshFilter), typeof(MeshRenderer))]
public class Experiment8Transform : MonoBehaviour
{
    private Mesh mesh;
    private Vector3[] originalVertices;
    private Material material;

    private void Start()
    {
        mesh = new Mesh { name = "Experiment 8 - 2D Triangle" };

        originalVertices = new Vector3[]
        {
            new Vector3(0.0f, 0.8f, 0.0f),
            new Vector3(-0.7f, -0.5f, 0.0f),
            new Vector3(0.7f, -0.5f, 0.0f)
        };

        mesh.vertices = originalVertices;
        mesh.triangles = new int[] { 0, 1, 2 };
        mesh.RecalculateBounds();
        mesh.RecalculateNormals();

        GetComponent<MeshFilter>().sharedMesh = mesh;

        Shader shader = Shader.Find("Custom/Experiment8");
        if (shader == null)
        {
            Debug.LogError("Experiment8 shader not found. Make sure Assets/Shaders/Experiment8.shader imported without errors.");
            enabled = false;
            return;
        }

        material = new Material(shader);
        GetComponent<MeshRenderer>().sharedMaterial = material;

        Debug.Log("Experiment 8 ready: T=Translation, R=Rotation, S=Scaling, F=Reflection, H=Shearing, Space=Reset.");
    }

    private void Update()
    {
        if (Input.GetKeyDown(KeyCode.T)) ApplyTranslation();
        if (Input.GetKeyDown(KeyCode.R)) ApplyRotation();
        if (Input.GetKeyDown(KeyCode.S)) ApplyScaling();
        if (Input.GetKeyDown(KeyCode.F)) ApplyReflection();
        if (Input.GetKeyDown(KeyCode.H)) ApplyShearing();
        if (Input.GetKeyDown(KeyCode.Space)) ResetShape();
    }

    // Apply a 2D homogeneous 3x3 transformation stored in Matrix4x4.
    private void ApplyTransformation(Matrix4x4 matrix)
    {
        Vector3[] transformed = new Vector3[originalVertices.Length];

        for (int i = 0; i < originalVertices.Length; i++)
        {
            Vector3 v = originalVertices[i];
            Vector4 p = new Vector4(v.x, v.y, 0f, 1f);
            Vector4 result = matrix * p;

            float w = Mathf.Abs(result.w) < 0.000001f ? 1f : result.w;
            transformed[i] = new Vector3(result.x / w, result.y / w, 0f);
        }

        mesh.vertices = transformed;
        mesh.RecalculateBounds();
        mesh.RecalculateNormals();
    }

    // 1. Translation: x' = x + tx, y' = y + ty.
    private void ApplyTranslation()
    {
        Matrix4x4 m = Matrix4x4.identity;
        m.m03 = 0.5f;
        m.m13 = 0.3f;
        ApplyTransformation(m);
        Debug.Log("Translation applied.");
    }

    // 2. Rotation counterclockwise by 45 degrees about the origin.
    private void ApplyRotation()
    {
        float angle = 45f * Mathf.Deg2Rad;
        float c = Mathf.Cos(angle);
        float s = Mathf.Sin(angle);

        Matrix4x4 m = Matrix4x4.identity;
        m.m00 = c;
        m.m01 = -s;
        m.m10 = s;
        m.m11 = c;

        ApplyTransformation(m);
        Debug.Log("Rotation by 45 degrees applied.");
    }

    // 3. Non-uniform scaling.
    private void ApplyScaling()
    {
        Matrix4x4 m = Matrix4x4.identity;
        m.m00 = 1.5f;
        m.m11 = 0.7f;
        ApplyTransformation(m);
        Debug.Log("Scaling applied.");
    }

    // 4. Reflection about the Y-axis: x' = -x, y' = y.
    private void ApplyReflection()
    {
        Matrix4x4 m = Matrix4x4.identity;
        m.m00 = -1f;
        ApplyTransformation(m);
        Debug.Log("Reflection about Y-axis applied.");
    }

    // 5. X-shear: x' = x + shx*y, y' = y.
    private void ApplyShearing()
    {
        Matrix4x4 m = Matrix4x4.identity;
        m.m01 = 0.5f;
        ApplyTransformation(m);
        Debug.Log("Shearing applied.");
    }

    private void ResetShape()
    {
        mesh.vertices = originalVertices;
        mesh.RecalculateBounds();
        mesh.RecalculateNormals();
        Debug.Log("Original triangle restored.");
    }

    private void OnDestroy()
    {
        if (mesh != null) Destroy(mesh);
        if (material != null) Destroy(material);
    }
}
