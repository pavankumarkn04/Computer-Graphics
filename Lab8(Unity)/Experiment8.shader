Shader "Custom/Experiment8"
{
    SubShader
    {
        Tags
        {
            "RenderType" = "Opaque"
            "Queue" = "Geometry"
        }

        Pass
        {
            Cull Off
            ZWrite On

            CGPROGRAM
            #pragma vertex vert
            #pragma fragment frag
            #include "UnityCG.cginc"

            struct appdata
            {
                float4 vertex : POSITION;
            };

            struct v2f
            {
                float4 vertex : SV_POSITION;
            };

            // Vertex shader: transforms object-space vertices to clip space.
            v2f vert(appdata input)
            {
                v2f output;
                output.vertex = UnityObjectToClipPos(input.vertex);
                return output;
            }

            // Fragment shader: outputs the triangle's green color.
            fixed4 frag(v2f input) : SV_Target
            {
                return fixed4(0.1, 0.8, 0.3, 1.0);
            }
            ENDCG
        }
    }
    FallBack "Unlit/Color"
}
