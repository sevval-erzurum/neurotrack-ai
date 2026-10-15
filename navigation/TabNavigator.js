import { createBottomTabNavigator } from "@react-navigation/bottom-tabs";

import ChatbotScreen from "../screens/ChatbotScreen";
import ChildAutismTestScreen from "../screens/ChildAutismTestScreen";
import DoctorNotesScreen from "../screens/DoctorNotesScreen";
import HomeScreen from "../screens/HomeScreen";
import NotificationsScreen from "../screens/NotificationsScreen";

const Tab = createBottomTabNavigator();

export default function TabNavigator({ user, onLogout }) {
  return (
    <Tab.Navigator
      screenOptions={{
        headerShown: true,
        tabBarActiveTintColor: "#2563EB",
        tabBarInactiveTintColor: "#6B7280",
      }}
    >
      <Tab.Screen name="Ana Sayfa">
        {() => (
          <HomeScreen
            user={user}
            onNavigate={() => {}}
            onLogout={onLogout}
          />
        )}
      </Tab.Screen>

      <Tab.Screen name="Doktor Notları">
        {() => <DoctorNotesScreen user={user} />}
      </Tab.Screen>

      <Tab.Screen name="Çocuk Testi">
        {() => <ChildAutismTestScreen user={user} />}
      </Tab.Screen>

      <Tab.Screen name="Chat">
        {() => (
          <ChatbotScreen
            user={user}
            onBack={() => {}}
          />
        )}
      </Tab.Screen>

      <Tab.Screen name="Bildirimler">
        {() => (
          <NotificationsScreen
            user={user}
            onBack={() => {}}
          />
        )}
      </Tab.Screen>
    </Tab.Navigator>
  );
}