/*

Author: Victor Faraut
Date: 28.10.2018


*/


using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class CubeMover : MonoBehaviour {

    private Vector3 currentRotVect = new Vector3(0,0,0);

	// Use this for initialization
	void Start () {
		
	}
	
	// Update is called once per frame
	void Update () {
        Move();
	}

    public void SetAngleXYZ(int euler, float angle)
    {
        if (euler == 0)
            currentRotVect[1] = angle;
        if (euler == 1)
            currentRotVect[0] = angle;
        if (euler == 2)
            currentRotVect[2] = -angle;
    }
    private void Move()
    {
        transform.eulerAngles = currentRotVect;
    }
}
