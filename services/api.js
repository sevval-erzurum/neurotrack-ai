export const API_URL = "http://192.168.1.9:8003";

export async function loginUser(email, password) {
  const response = await fetch(`${API_URL}/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });

  const data = await response.json();
  return { response, data };
}

export async function registerUser(fullName, email, password, role) {
  const response = await fetch(`${API_URL}/register`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      full_name: fullName,
      email,
      password,
      role,
    }),
  });

  const data = await response.json();
  return { response, data };
}

export async function sendChatMessage(userId, message, role) {
  const response = await fetch(`${API_URL}/chatbot`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      user_id: userId,
      message,
      role,
    }),
  });

  const data = await response.json();
  return { response, data };
}

export async function getNotifications(userId) {
  const response = await fetch(`${API_URL}/notifications?user_id=${userId}`);
  const data = await response.json();
  return { response, data };
}

export async function markNotificationRead(notificationId) {
  const response = await fetch(
    `${API_URL}/mark-notification-read?notification_id=${notificationId}`,
    { method: "POST" }
  );

  const data = await response.json();
  return { response, data };
}

export async function createDailyLog(
  userId,
  mood,
  sleepHours,
  socialInteraction,
  note
) {
  const response = await fetch(`${API_URL}/daily-log`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      user_id: userId,
      mood,
      sleep_hours: sleepHours,
      social_interaction: socialInteraction,
      note,
    }),
  });

  const data = await response.json();
  return { response, data };
}

export async function getDailyLogs(userId) {
  const response = await fetch(`${API_URL}/my-daily-logs?user_id=${userId}`);
  const data = await response.json();
  return { response, data };
}

export async function getDailyLogAnalysis(userId) {
  const response = await fetch(
    `${API_URL}/daily-log-analysis?user_id=${userId}`
  );
  const data = await response.json();
  return { response, data };
}

export async function getRiskAlert(userId) {
  const response = await fetch(`${API_URL}/risk-alert?user_id=${userId}`);
  const data = await response.json();
  return { response, data };
}

export async function getChildren(parentId) {
  const response = await fetch(`${API_URL}/children?parent_id=${parentId}`);
  const data = await response.json();
  return { response, data };
}

export async function createChild(parentId, name, age, gender) {
  const response = await fetch(`${API_URL}/children`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      parent_id: parentId,
      name,
      age,
      gender,
    }),
  });

  const data = await response.json();
  return { response, data };
}

export async function createChildDailyLog(
  childId,
  mood,
  sleepHours,
  socialInteraction,
  note
) {
  const response = await fetch(`${API_URL}/child-daily-log`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      child_id: childId,
      mood,
      sleep_hours: sleepHours,
      social_interaction: socialInteraction,
      note,
    }),
  });

  const data = await response.json();
  return { response, data };
}

export async function getChildDailyLogs(childId) {
  const response = await fetch(
    `${API_URL}/child-daily-logs?child_id=${childId}`
  );
  const data = await response.json();
  return { response, data };
}

export async function createChildClinicalFollowUp(
  childId,
  meltdown,
  sensorySensitivity,
  eyeContact,
  communicationWillingness,
  routineReaction,
  eatingPattern,
  medicationTherapy,
  note
) {
  const response = await fetch(`${API_URL}/child-clinical-followup`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      child_id: childId,
      meltdown,
      sensory_sensitivity: sensorySensitivity,
      eye_contact: eyeContact,
      communication_willingness: communicationWillingness,
      routine_reaction: routineReaction,
      eating_pattern: eatingPattern,
      medication_therapy: medicationTherapy,
      note,
    }),
  });

  const data = await response.json();
  return { response, data };
}

export async function getChildClinicalFollowUps(childId) {
  const response = await fetch(
    `${API_URL}/child-clinical-followups?child_id=${childId}`
  );
  const data = await response.json();
  return { response, data };
}

export async function getChildAlerts(childId) {
  const response = await fetch(`${API_URL}/child-alerts?child_id=${childId}`);
  const data = await response.json();
  return { response, data };
}

export async function getMyPatients(doctorId) {
  const response = await fetch(`${API_URL}/my-patients?doctor_id=${doctorId}`);
  const data = await response.json();
  return { response, data };
}

export async function getMyChildPatients(doctorId) {
  const response = await fetch(
    `${API_URL}/my-child-patients?doctor_id=${doctorId}`
  );
  const data = await response.json();
  return { response, data };
}

export async function addPatientToDoctor(doctorId, patientId) {
  const response = await fetch(
    `${API_URL}/add-patient?doctor_id=${doctorId}&patient_id=${patientId}`,
    {
      method: "POST",
    }
  );

  const data = await response.json();
  return { response, data };
}

export async function addChildPatientToDoctor(doctorId, childId) {
  const response = await fetch(
    `${API_URL}/add-child-patient?doctor_id=${doctorId}&child_id=${childId}`,
    {
      method: "POST",
    }
  );

  const data = await response.json();
  return { response, data };
}

export async function getPatientDetails(patientId) {
  const response = await fetch(
    `${API_URL}/patient-details?patient_id=${patientId}`
  );
  const data = await response.json();
  return { response, data };
}

export async function getPatientAnalysis(patientId) {
  const response = await fetch(
    `${API_URL}/patient-ai-summary?patient_id=${patientId}`
  );
  const data = await response.json();
  return { response, data };
}

export async function getChildPatientDetails(childId) {
  const response = await fetch(
    `${API_URL}/child-patient-details?child_id=${childId}`
  );
  const data = await response.json();
  return { response, data };
}

export async function createDoctorNote(
  doctorId,
  patientId,
  childId,
  note,
  recommendation,
  nextVisitDate
) {
  const response = await fetch(`${API_URL}/doctor-note`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      doctor_id: doctorId,
      patient_id: patientId,
      child_id: childId,
      note,
      recommendation,
      next_visit_date: nextVisitDate,
    }),
  });

  const data = await response.json();
  return { response, data };
}

export async function getDoctorNotesForPatient(patientId) {
  const response = await fetch(
    `${API_URL}/doctor-notes?patient_id=${patientId}`
  );
  const data = await response.json();
  return { response, data };
}

export async function getDoctorNotesForChild(childId) {
  const response = await fetch(`${API_URL}/doctor-notes?child_id=${childId}`);
  const data = await response.json();
  return { response, data };
}
export async function sendMessage(senderId, receiverId, content) {
  const response = await fetch(`${API_URL}/send-message`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      sender_id: senderId,
      receiver_id: receiverId,
      content,
    }),
  });

  const data = await response.json();
  return { response, data };
}

export async function getMyMessages(userId) {
  const response = await fetch(`${API_URL}/my-messages?user_id=${userId}`);
  const data = await response.json();
  return { response, data };
}

export async function getConversation(user1Id, user2Id) {
  const response = await fetch(
    `${API_URL}/conversation?user1_id=${user1Id}&user2_id=${user2Id}`
  );

  const data = await response.json();
  return { response, data };
}

export async function markMessageRead(messageId) {
  const response = await fetch(
    `${API_URL}/mark-message-read?message_id=${messageId}`,
    {
      method: "POST",
    }
  );

  const data = await response.json();
  return { response, data };
}
export async function getAvailableDoctorsForMessage(userId) {
  const response = await fetch(
    `${API_URL}/available-doctors-for-message?user_id=${userId}`
  );
  const data = await response.json();
  return { response, data };
}

export async function sendMessageRequest(senderId, receiverId) {
  const response = await fetch(`${API_URL}/send-message-request`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      sender_id: senderId,
      receiver_id: receiverId,
    }),
  });

  const data = await response.json();
  return { response, data };
}

export async function getMessageRequests(userId) {
  const response = await fetch(`${API_URL}/message-requests?user_id=${userId}`);
  const data = await response.json();
  return { response, data };
}

export async function respondMessageRequest(requestId, status, userId) {
  const response = await fetch(
    `${API_URL}/respond-message-request?request_id=${requestId}&status=${status}&user_id=${userId}`,
    {
      method: "POST",
    }
  );

  const data = await response.json();
  return { response, data };
}

export async function getMessageContacts(userId) {
  const response = await fetch(`${API_URL}/message-contacts?user_id=${userId}`);
  const data = await response.json();
  return { response, data };
}

export async function secureSendMessage(senderId, receiverId, content) {
  const response = await fetch(`${API_URL}/secure-send-message`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      sender_id: senderId,
      receiver_id: receiverId,
      content,
    }),
  });

  const data = await response.json();
  return { response, data };
}

export async function secureConversation(user1Id, user2Id) {
  const response = await fetch(
    `${API_URL}/secure-conversation?user1_id=${user1Id}&user2_id=${user2Id}`
  );

  const data = await response.json();
  return { response, data };
}
export async function getSmartNotifications(userId) {
  const response = await fetch(`${API_URL}/smart-notifications?user_id=${userId}`);
  const data = await response.json();
  return { response, data };
}
export async function deleteChild(childId, parentId) {
  const response = await fetch(
    `${API_URL}/delete-child?child_id=${childId}&parent_id=${parentId}`,
    {
      method: "DELETE",
    }
  );

  const data = await response.json();
  return { response, data };
}

export async function removePatientFromDoctor(doctorId, patientId) {
  const response = await fetch(
    `${API_URL}/remove-patient-from-doctor?doctor_id=${doctorId}&patient_id=${patientId}`,
    {
      method: "DELETE",
    }
  );

  const data = await response.json();
  return { response, data };
}

export async function removeChildPatientFromDoctor(doctorId, childId) {
  const response = await fetch(
    `${API_URL}/remove-child-patient-from-doctor?doctor_id=${doctorId}&child_id=${childId}`,
    {
      method: "DELETE",
    }
  );

  const data = await response.json();
  return { response, data };
}
export async function getAdultGamification(userId) {
  const response = await fetch(`${API_URL}/adult-gamification-v2?user_id=${userId}`);
  const data = await response.json();
  return { response, data };
}
export async function createChildAutismTest(childId, answers, age) {
  const response = await fetch(`${API_URL}/child-autism-test`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      child_id: childId,
      A1_Score: answers.A1_Score,
      A2_Score: answers.A2_Score,
      A3_Score: answers.A3_Score,
      A4_Score: answers.A4_Score,
      A5_Score: answers.A5_Score,
      A6_Score: answers.A6_Score,
      A7_Score: answers.A7_Score,
      A8_Score: answers.A8_Score,
      A9_Score: answers.A9_Score,
      A10_Score: answers.A10_Score,
      age,
    }),
  });

  const data = await response.json();
  return { response, data };
}

export async function getChildAutismTests(childId) {
  const response = await fetch(`${API_URL}/child-autism-tests?child_id=${childId}`);
  const data = await response.json();
  return { response, data };
}