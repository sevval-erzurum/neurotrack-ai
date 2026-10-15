import { useState } from "react";
import {
    Alert,
    Pressable,
    SafeAreaView,
    ScrollView,
    StyleSheet,
    Text,
    TextInput,
    View,
} from "react-native";

import AppBrandHeader from "../components/AppBrandHeader";
import { registerUser } from "../services/api";

const COLORS = {
  primary: "#2563EB",
  white: "#FFFFFF",
  dark: "#111827",
  gray: "#6B7280",
  lightGray: "#F3F4F6",
  border: "#CBD5E1",
  card: "#FFFFFF",
  blueSoft: "#EFF6FF",
};

export default function RegisterScreen({ onBackToLogin }) {
  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [role, setRole] = useState("adult");

  async function handleRegister() {
    if (!fullName.trim()) {
      Alert.alert("Eksik bilgi", "Ad soyad alanını doldur.");
      return;
    }

    if (!email.includes("@")) {
      Alert.alert("Hatalı email", "Geçerli bir email adresi gir.");
      return;
    }

    if (password.length < 4) {
      Alert.alert("Hatalı şifre", "Şifre en az 4 karakter olmalı.");
      return;
    }

    try {
      const { response, data } = await registerUser(
        fullName,
        email,
        password,
        role
      );

      if (response.ok) {
        Alert.alert(
          "Kayıt başarılı",
          "Hesabın oluşturuldu. Şimdi giriş yapabilirsin."
        );
        onBackToLogin();
      } else {
        Alert.alert(
          "Kayıt hatası",
          data.detail ? String(data.detail) : JSON.stringify(data)
        );
      }
    } catch (error) {
      Alert.alert("Bağlantı hatası", String(error));
    }
  }

  function RoleButton({ value, label }) {
    const selected = role === value;

    return (
      <Pressable
        style={selected ? styles.selectedRole : styles.roleButton}
        onPress={() => setRole(value)}
      >
        <Text style={selected ? styles.selectedRoleText : styles.roleText}>
          {label}
        </Text>
      </Pressable>
    );
  }

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView contentContainerStyle={styles.scrollContent}>
        <View style={styles.card}>
          <AppBrandHeader small />

          <Text style={styles.screenTitle}>Kayıt Ol</Text>
          <Text style={styles.screenSubtitle}>
            Sisteme rolüne uygun hesap oluşturarak başlayabilirsin.
          </Text>

          <TextInput
            placeholder="Ad Soyad"
            placeholderTextColor={COLORS.gray}
            value={fullName}
            onChangeText={setFullName}
            style={styles.input}
          />

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

          <Text style={styles.label}>Kullanıcı Rolü</Text>

          <View style={styles.roleRow}>
            <RoleButton value="adult" label="Adult" />
            <RoleButton value="parent" label="Parent" />
            <RoleButton value="doctor" label="Doctor" />
          </View>

          <View style={styles.roleInfo}>
            <Text style={styles.roleInfoText}>
              Adult: bireysel takip • Parent: çocuk takibi • Doctor: hasta takibi
            </Text>
          </View>

          <Pressable style={styles.button} onPress={handleRegister}>
            <Text style={styles.buttonText}>Kayıt Ol</Text>
          </Pressable>

          <Pressable style={styles.backButton} onPress={onBackToLogin}>
            <Text style={styles.buttonText}>Giriş Ekranına Dön</Text>
          </Pressable>

          <Text style={styles.disclaimer}>
            Bu sistem tanı koymaz. Uzman değerlendirmesinin yerine geçmez.
          </Text>
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: COLORS.lightGray,
  },
  scrollContent: {
    padding: 22,
    paddingBottom: 40,
  },
  card: {
    backgroundColor: COLORS.card,
    borderRadius: 24,
    padding: 24,
    marginTop: 18,
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
  label: {
    fontSize: 14,
    fontWeight: "900",
    color: COLORS.dark,
    marginBottom: 8,
  },
  roleRow: {
    flexDirection: "row",
    gap: 8,
    marginBottom: 12,
  },
  roleButton: {
    flex: 1,
    borderWidth: 1,
    borderColor: COLORS.border,
    padding: 12,
    borderRadius: 12,
    alignItems: "center",
  },
  selectedRole: {
    flex: 1,
    backgroundColor: COLORS.primary,
    padding: 12,
    borderRadius: 12,
    alignItems: "center",
  },
  roleText: {
    color: COLORS.dark,
    fontWeight: "900",
  },
  selectedRoleText: {
    color: COLORS.white,
    fontWeight: "900",
  },
  roleInfo: {
    backgroundColor: COLORS.blueSoft,
    padding: 12,
    borderRadius: 12,
    marginBottom: 14,
  },
  roleInfoText: {
    color: COLORS.primary,
    fontSize: 12,
    lineHeight: 18,
    textAlign: "center",
    fontWeight: "700",
  },
  button: {
    backgroundColor: COLORS.primary,
    padding: 15,
    borderRadius: 14,
    alignItems: "center",
    marginTop: 8,
  },
  backButton: {
    backgroundColor: COLORS.dark,
    padding: 15,
    borderRadius: 14,
    alignItems: "center",
    marginTop: 10,
  },
  buttonText: {
    color: COLORS.white,
    fontSize: 17,
    fontWeight: "900",
  },
  disclaimer: {
    marginTop: 18,
    fontSize: 12,
    color: COLORS.gray,
    textAlign: "center",
    lineHeight: 18,
  },
});