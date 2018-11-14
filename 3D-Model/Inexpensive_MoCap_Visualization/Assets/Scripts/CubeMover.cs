/*

Author: Victor Faraut
Date: 28.10.2018


*/


using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class CubeMover : MonoBehaviour {

    private Vector3 currentPos = new Vector3(0, 0.5f, 0);
    private Vector3 currentRotVect = new Vector3(0,0,0);
    private Quaternion currentQuaternion = new Quaternion(0, 0, 0, 0);

	// Use this for initialization
	void Start () {
		
	}
	
	// Update is called once per frame
	void FixedUpdate () {
        Move();
	}

    public void SetAngleXYZ(int euler, float angle)
    {
        if (euler == 0)
            currentRotVect.x = angle;
        if (euler == 1)
            currentRotVect.y = angle;
        if (euler == 2)
            currentRotVect.z = -angle;
    }
    public void SetAngleXYZW(int quat, float angle)
    {
        if (quat == 2)
            currentQuaternion.x = angle;
        if (quat == 1)
            currentQuaternion.y = angle;
        if (quat == 4)
            currentQuaternion.z = angle;
        if (quat == 3)
            currentQuaternion.w = angle;

    }
    private void Move()
    {
        transform.SetPositionAndRotation(currentPos, currentQuaternion);
    }
}
