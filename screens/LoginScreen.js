import { useState } from "react";
import {
  Alert,
  Pressable,
  SafeAreaView,
  StyleSheet,
  Text,
  TextInput,
  View,
} from "react-native";

import AppBrandHeader from "../components/AppBrandHeader";
import { API_URL, loginUser } from "../services/api";

const COLORS = {
  primary: "#2563EB",
  white: "#FFFFFF",
  dark: "#111827",
  gray: "#6B7280",
  lightGray: "#F3F4F6",
  border: "#CBD5E1",
  card: "#FFFFFF",
};

export default function LoginScreen({ onLogin, onRegisterNavigate }) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  async function handleLogin() {
    if (!email.includes("@")) {
      Alert.alert("Hatalı email", "Lütfen geçerli bir email adresi gir.");
      return;
    }

    if (!password) {
      Alert.alert("Eksik şifre", "Lütfen şifreni gir.");
      return;
    }

    try {
      const { response, data } = await loginUser(email, password);

      if (response.ok) {
        onLogin(data);
      } else {
        Alert.alert(
          "Giriş hatası",
          data.detail ? String(data.detail) : JSON.stringify(data)
        );
      }
    } catch (error) {
      Alert.alert(
        "Bağlantı hatası",
        `API adresi: ${API_URL}\n\nHata: ${String(error)}`
      );
    }
  }

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.card}>
        <AppBrandHeader />

        <Text style={styles.screenTitle}>Giriş Yap</Text>
        <Text style={styles.screenSubtitle}>
          Hesabına giriş yaparak takip paneline erişebilirsin.
        </Text>

        <TextInput
          placeholder="Email"
          placeholderTextColor={COLORS.gray}
          value={email}
          onChangeText={setEmail}
          autoCapitalize="none"
          keyboardType="email-address"
          style={styles.input}
        />

        <TextInput
          placeholder="Şifre"
          placeholderTextColor={COLORS.gray}
          value={password}
          onChangeText={setPassword}
          secureTextEntry
          style={styles.input}
        />

        <Pressable style={styles.button} onPress={handleLogin}>
          <Text style={styles.buttonText}>Giriş Yap</Text>
        </Pressable>

        <Pressable style={styles.registerButton} onPress={onRegisterNavigate}>
          <Text style={styles.registerButtonText}>Hesabın yok mu? Kayıt Ol</Text>
        </Pressable>

        <Text style={styles.disclaimer}>
          Bu sistem tanı koymaz. Takip, ön değerlendirme ve karar desteği amacıyla kullanılır.
        </Text>
      </View>

      <Text style={styles.apiText}>API: {API_URL}</Text>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: COLORS.lightGray,
    justifyContent: "center",
    padding: 22,
  },
  card: {
    backgroundColor: COLORS.card,
    borderRadius: 24,
    padding: 24,
  },
  screenTitle: {
    fontSize: 22,
    fontWeight: "900",
    color: COLORS.dark,
    textAlign: "center",
    marginBottom: 6,
  },
  screenSubtitle: {
    fontSize: 14,
    color: COLORS.gray,
    textAlign: "center",
    lineHeight: 20,
    marginBottom: 18,
  },
  input: {
    backgroundColor: COLORS.white,
    borderWidth: 1,
    borderColor: COLORS.border,
    borderRadius: 14,
    padding: 14,
    marginBottom: 12,
    fontSize: 16,
    color: COLORS.dark,
  },
  button: {
    backgroundColor: COLORS.primary,
    padding: 15,
    borderRadius: 14,
    alignItems: "center",
    marginTop: 8,
  },
  registerButton: {
    backgroundColor: COLORS.white,
    borderWidth: 1,
    borderColor: COLORS.primary,
    padding: 14,
    borderRadius: 14,
    alignItems: "center",
    marginTop: 10,
  },
  buttonText: {
    color: COLORS.white,
    fontSize: 17,
    fontWeight: "900",
  },
  registerButtonText: {
    color: COLORS.primary,
    fontSize: 16,
    fontWeight: "900",
  },
  disclaimer: {
    marginTop: 18,
    fontSize: 12,
    color: COLORS.gray,
    textAlign: "center",
    lineHeight: 18,
  },
  apiText: {
    fontSize: 11,
    color: COLORS.gray,
    textAlign: "center",
    marginTop: 12,
  },
});