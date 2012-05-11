// The infinite frustum set-up code.
matrix4f infinite_frustum(float left, float right,
						  float bottom, float top,
						  float zNear)
{
	matrix4f m;
	m.make_identity();
	
	m(0,0) = (2*zNear) / (right - left);
	m(0,2) = (right + left) / (right - left);
	
	m(1,1) = (2*zNear) / (top - bottom);
	m(1,2) = (top + bottom) / (top - bottom);
	
    float nudge = 1.0;
    
    if(b['j'])    // nudge infinity in some in case of lsb slop
        nudge = 0.999;


	m(2,2) = -1  * nudge;
	m(2,3) = -2*zNear * nudge;
	
	m(3,2) = -1;
	m(3,3) = 0;
	
	return m;
}

inline matrix4f infinite_frustum_inverse(float left, float right,
								float bottom, float top,
								float zNear)
{
	matrix4f m;
	m.make_identity();
	
	m(0,0) = (right - left) / (2 * zNear);
	m(0,3) = (right + left) / (2 * zNear);
	
	m(1,1) = (top - bottom) / (2 * zNear);
	m(1,3) = (top + bottom) / (2 * zNear);
	
	m(2,2) = 0;
	m(2,3) = -1;
	
	m(3,2) = -1 / (2 * zNear);
	m(3,3) = 1 / (2 * zNear);
	
	return m;
}

matrix4f infinite_perspective(float fovy, float aspect, float zNear)
{
	double tangent = tan(to_radians(fovy/2.0));
	float y = tangent * zNear;
	float x = aspect * y;
	return infinite_frustum(-x, x, -y, y, zNear);
}

inline matrix4f infinite_perspective_inverse(float fovy, float aspect, float zNear)
{
	double tangent = tan(to_radians(fovy/2.0));
	float y = tangent * zNear;
	float x = aspect * y;
	return infinite_frustum_inverse(-x, x, -y, y, zNear);
}

void apply_infinite_perspective(glut_perspective_reshaper & r)
{
	r.aspect = r.aspect_factor * float(r.width)/float(r.height);
	if ( r.aspect < 1 )
	{
		float fovx = r.fovy; 
		float real_fov = to_degrees(2 * atan(tan(to_radians(fovx/2))/r.aspect));
		glMultMatrixf(infinite_perspective(real_fov, r.aspect, r.zNear).m);
	}
	else
		glMultMatrixf(infinite_perspective(r.fovy, r.aspect, r.zNear).m);
}

////// CALL!!!
glMatrixMode(GL_PROJECTION);
glLoadIdentity();

apply_infinite_perspective(reshaper);
glMatrixMode(GL_MODELVIEW);