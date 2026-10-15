import { useState } from "react";

import AISuggestionScreen from "../../screens/AISuggestionScreen";
import AnalyticsScreen from "../../screens/AnalyticsScreen";
import ChatbotScreen from "../../screens/ChatbotScreen";
import ChildAlertScreen from "../../screens/ChildAlertScreen";
import ChildClinicalScreen from "../../screens/ChildClinicalScreen";
import ChildDailyLogScreen from "../../screens/ChildDailyLogScreen";
import ChildPatientDetailScreen from "../../screens/ChildPatientDetailScreen";
import DailyLogScreen from "../../screens/DailyLogScreen";
import DoctorPanelScreen from "../../screens/DoctorPanelScreen";
import HomeScreen from "../../screens/HomeScreen";
import LoginScreen from "../../screens/LoginScreen";
import MessageScreen from "../../screens/MessageScreen";
import NotificationsScreen from "../../screens/NotificationsScreen";
import ParentPanelScreen from "../../screens/ParentPanelScreen";
import PatientAnalysisScreen from "../../screens/PatientAnalysisScreen";
import PatientDetailScreen from "../../screens/PatientDetailScreen";
import ProfileScreen from "../../screens/ProfileScreen";
import RegisterScreen from "../../screens/RegisterScreen";
import RiskScreen from "../../screens/RiskScreen";

export default function IndexScreen() {
  const [user, setUser] = useState<any>(null);
  const [screen, setScreen] = useState<string>("home");

  const [selectedPatient, setSelectedPatient] = useState<any>(null);
  const [analysisPatient, setAnalysisPatient] = useState<any>(null);
  const [selectedChild, setSelectedChild] = useState<any>(null);
  const [selectedChildPatient, setSelectedChildPatient] = useState<any>(null);

  function handleLogin(loggedInUser: any) {
    setUser(loggedInUser);
    setScreen("home");
  }

  function handleLogout() {
    setUser(null);
    setScreen("home");
    setSelectedPatient(null);
    setAnalysisPatient(null);
    setSelectedChild(null);
    setSelectedChildPatient(null);
  }

  if (!user && screen === "register") {
    return <RegisterScreen onBackToLogin={() => setScreen("home")} />;
  }

  if (!user) {
    return (
      <LoginScreen
        onLogin={handleLogin}
        onRegisterNavigate={() => setScreen("register")}
      />
    );
  }

  if (screen === "profile") {
    return <ProfileScreen user={user} onBack={() => setScreen("home")} />;
  }

  if (screen === "messages") {
    return <MessageScreen user={user} onBack={() => setScreen("home")} />;
  }

  if (screen === "dailyLog") {
    return <DailyLogScreen user={user} onBack={() => setScreen("home")} />;
  }

  if (screen === "aiSuggestion") {
    return <AISuggestionScreen user={user} onBack={() => setScreen("home")} />;
  }

  if (screen === "analytics") {
    return <AnalyticsScreen user={user} onBack={() => setScreen("home")} />;
  }

  if (screen === "risk") {
    return <RiskScreen user={user} onBack={() => setScreen("home")} />;
  }

  if (screen === "chatbot") {
    return <ChatbotScreen user={user} onBack={() => setScreen("home")} />;
  }

  if (screen === "notifications") {
    return <NotificationsScreen user={user} onBack={() => setScreen("home")} />;
  }

  if (screen === "childDailyLog" && selectedChild) {
    return (
      <ChildDailyLogScreen
        child={selectedChild}
        onBack={() => setScreen("parentPanel")}
      />
    );
  }

  if (screen === "childClinical" && selectedChild) {
    return (
      <ChildClinicalScreen
        child={selectedChild}
        onBack={() => setScreen("parentPanel")}
      />
    );
  }

  if (screen === "childAlert" && selectedChild) {
    return (
      <ChildAlertScreen
        child={selectedChild}
        onBack={() => setScreen("parentPanel")}
      />
    );
  }

  if (screen === "parentPanel") {
    return (
      <ParentPanelScreen
        user={user}
        onBack={() => setScreen("home")}
        onOpenChild={(child: any) => {
          setSelectedChild(child);
          setScreen("childDailyLog");
        }}
        onOpenChildClinical={(child: any) => {
          setSelectedChild(child);
          setScreen("childClinical");
        }}
        onOpenChildAlert={(child: any) => {
          setSelectedChild(child);
          setScreen("childAlert");
        }}
      />
    );
  }

  if (screen === "patientAnalysis" && analysisPatient) {
    return (
      <PatientAnalysisScreen
        patient={analysisPatient}
        onBack={() => setScreen("patientDetail")}
      />
    );
  }

  if (screen === "patientDetail" && selectedPatient) {
    return (
      <PatientDetailScreen
        patient={selectedPatient}
        doctor={user}
        onBack={() => setScreen("doctorPanel")}
        onOpenAnalysis={(patient: any) => {
          setAnalysisPatient(patient);
          setScreen("patientAnalysis");
        }}
      />
    );
  }

  if (screen === "childPatientDetail" && selectedChildPatient) {
    return (
      <ChildPatientDetailScreen
        child={selectedChildPatient}
        doctor={user}
        onBack={() => setScreen("doctorPanel")}
      />
    );
  }

  if (screen === "doctorPanel") {
    return (
      <DoctorPanelScreen
        user={user}
        onBack={() => setScreen("home")}
        onOpenPatient={(patient: any) => {
          setSelectedPatient(patient);
          setScreen("patientDetail");
        }}
        onOpenChildPatient={(child: any) => {
          setSelectedChildPatient(child);
          setScreen("childPatientDetail");
        }}
      />
    );
  }

  return (
    <HomeScreen
      user={user}
      onNavigate={setScreen}
      onLogout={handleLogout}
    />
  );
}