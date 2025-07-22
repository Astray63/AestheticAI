import { http, HttpResponse } from 'msw';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

export const handlers = [
  // Auth
  http.post(`${API_BASE_URL}/auth/login`, () => {
    return HttpResponse.json({
      access_token: 'mock-jwt-token',
      token_type: 'bearer',
      user: {
        id: '1',
        username: 'doctor_test',
        specialty: 'Médecine Esthétique'
      }
    });
  }),

  // Patients
  http.post(`${API_BASE_URL}/patients`, () => {
    return HttpResponse.json({
      id: 'patient-123',
      age: 35,
      gender: 'female',
      skin_type: 'normal',
      created_at: new Date().toISOString()
    }, { status: 201 });
  }),

  http.get(`${API_BASE_URL}/patients`, () => {
    return HttpResponse.json([
      {
        id: 'patient-123',
        age: 35,
        gender: 'female',
        skin_type: 'normal',
        created_at: new Date().toISOString()
      }
    ]);
  }),

  // Simulations
  http.post(`${API_BASE_URL}/simulations`, () => {
    return HttpResponse.json({
      id: 'simulation-456',
      patient_id: 'patient-123',
      intervention_type: 'lips',
      dose: 2.0,
      original_image_url: '/uploads/original_123.jpg',
      result_image_url: '/uploads/result_123.jpg',
      status: 'completed',
      created_at: new Date().toISOString()
    }, { status: 201 });
  }),

  http.get(`${API_BASE_URL}/simulations/:id`, ({ params }) => {
    const { id } = params;
    return HttpResponse.json({
      id,
      patient_id: 'patient-123',
      intervention_type: 'lips',
      dose: 2.0,
      original_image_url: '/uploads/original_123.jpg',
      result_image_url: '/uploads/result_123.jpg',
      status: 'completed',
      created_at: new Date().toISOString()
    });
  }),

  // Image upload
  http.post(`${API_BASE_URL}/upload`, () => {
    return HttpResponse.json({
      filename: 'uploaded_image_123.jpg',
      url: '/uploads/uploaded_image_123.jpg'
    });
  }),

  // Error cases
  http.post(`${API_BASE_URL}/simulations/error`, () => {
    return HttpResponse.json({
      detail: 'AI processing failed'
    }, { status: 500 });
  }),

  http.post(`${API_BASE_URL}/simulations/timeout`, () => {
    return HttpResponse.json({
      detail: 'AI processing timeout'
    }, { status: 504 });
  })
];
