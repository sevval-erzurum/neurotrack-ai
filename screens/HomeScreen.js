import { useEffect, useState } from "react";
import {
  Pressable,
  SafeAreaView,
  ScrollView,
  StyleSheet,
  Text,
  View,
} from "react-native";

import { getAdultGamification } from "../services/api";

export default function HomeScreen({ user, onNavigate, onLogout }) {
  const [motivation, setMotivation] = useState(null);

  function getRoleTitle(role) {
    if (role === "adult") return "Yetişkin Kullanıcı Paneli";
    if (role === "parent") return "Ebeveyn Paneli";
    if (role === "doctor") return "Doktor Paneli";
    return "Kullanıcı Paneli";
  }

  function getRoleDescription(role) {
    if (role === "adult") {
      return "Günlük kayıt, gelişim grafiği, risk analizi, mesajlaşma ve DEVA AI asistanını buradan kullanabilirsiniz.";
    }

    if (role === "parent") {
      return "Çocuk ekleme, çocuk günlük kayıt, klinik takip, uyarı analizi, mesajlaşma ve DEVA AI asistanını buradan kullanabilirsiniz.";
    }

    if (role === "doctor") {
      return "Yetişkin ve çocuk hasta takibi, doktor notları, AI analiz, hasta mesajları ve klinik değerlendirme ekranlarını buradan kullanabilirsiniz.";
    }

    return "Sisteme hoş geldiniz.";
  }

  function getRoleBadgeColor(role) {
    if (role === "adult") return "#2563EB";
    if (role === "parent") return "#059669";
    if (role === "doctor") return "#7C3AED";
    return "#374151";
  }

  async function loadMotivation() {
    if (user.role !== "adult") return;

    try {
      const { response, data } = await getAdultGamification(user.user_id);

      if (response.ok) {
        setMotivation(data);
      }
    } catch (error) {
      console.log("Motivasyon bilgisi alınamadı:", error);
    }
  }

  useEffect(() => {
    loadMotivation();
  }, []);

  function getBadgeNames() {
    if (!motivation || !motivation.badges || motivation.badges.length === 0) {
      return "Henüz rozet yok";
    }

    return motivation.badges.map((badge) => badge.title).join(", ");
  }

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView contentContainerStyle={styles.scrollContent}>
        <View style={styles.card}>
          <Text style={styles.title}>Otizm Takip Sistemi</Text>
          <Text style={styles.welcome}>Hoş geldin</Text>
          <Text style={styles.name}>{user.full_name}</Text>

          <View
            style={[
              styles.roleBox,
              { borderLeftColor: getRoleBadgeColor(user.role) },
            ]}
          >
            <Text style={styles.roleLabel}>Aktif Rol</Text>
            <Text style={styles.roleValue}>{getRoleTitle(user.role)}</Text>
          </View>

          <Text style={styles.description}>{getRoleDescription(user.role)}</Text>

          {user.role === "adult" && (
            <View style={styles.motivationCard}>
              <Text style={styles.motivationTitle}>
                Günlük Takip Motivasyonu
              </Text>

              <Text style={styles.streakText}>
                🔥 {motivation ? motivation.current_streak : 0} günlük seri
              </Text>

              <Text style={styles.badgeText}>
                🏅 Rozetlerin: {getBadgeNames()}
              </Text>

              <Text style={styles.motivationMessage}>
                {motivation
                  ? motivation.message
                  : "Günlük kayıt girerek serini başlatabilirsin."}
              </Text>

              <Pressable style={styles.smallRefreshButton} onPress={loadMotivation}>
                <Text style={styles.smallRefreshText}>Seriyi Yenile</Text>
              </Pressable>
            </View>
          )}

          <Pressable
            style={styles.profileButton}
            onPress={() => onNavigate("profile")}
          >
            <Text style={styles.buttonText}>Profilim</Text>
          </Pressable>

          {user.role === "adult" && (
            <>
              <Text style={styles.groupTitle}>Yetişkin Takip İşlemleri</Text>

              <Pressable
                style={styles.button}
                onPress={() => onNavigate("dailyLog")}
              >
                <Text style={styles.buttonText}>Günlük Kayıt</Text>
              </Pressable>

              <Pressable
                style={styles.button}
                onPress={() => onNavigate("analytics")}
              >
                <Text style={styles.buttonText}>Gelişim Grafiği</Text>
              </Pressable>

              <Pressable
                style={styles.riskButton}
                onPress={() => onNavigate("risk")}
              >
                <Text style={styles.buttonText}>Risk Analizi</Text>
              </Pressable>
            </>
          )}

          {user.role === "parent" && (
            <>
              <Text style={styles.groupTitle}>Ebeveyn İşlemleri</Text>

              <Pressable
                style={styles.button}
                onPress={() => onNavigate("parentPanel")}
              >
                <Text style={styles.buttonText}>Parent Paneli</Text>
              </Pressable>
            </>
          )}

          {user.role === "doctor" && (
            <>
              <Text style={styles.groupTitle}>Doktor İşlemleri</Text>

              <Pressable
                style={styles.button}
                onPress={() => onNavigate("doctorPanel")}
              >
                <Text style={styles.buttonText}>Doktor Paneli</Text>
              </Pressable>
            </>
          )}

          <Text style={styles.groupTitle}>İletişim</Text>

          <Pressable
            style={styles.messageButton}
            onPress={() => onNavigate("messages")}
          >
            <Text style={styles.buttonText}>
              {user.role === "doctor"
                ? "Hasta Mesajları"
                : "Doktora Mesaj Gönder"}
            </Text>
          </Pressable>

          <Text style={styles.groupTitle}>Genel İşlemler</Text>

          <Pressable
            style={styles.notificationButton}
            onPress={() => onNavigate("notifications")}
          >
            <Text style={styles.buttonText}>Bildirimlerim</Text>
          </Pressable>

          <Pressable style={styles.logoutButton} onPress={onLogout}>
            <Text style={styles.buttonText}>Çıkış Yap</Text>
          </Pressable>

          <Text style={styles.note}>
            Bu sistem tanı koymaz. Takip, analiz ve karar desteği amacıyla kullanılır.
          </Text>
        </View>
      </ScrollView>

      <Pressable
        style={styles.floatingAiButton}
        onPress={() => onNavigate("chatbot")}
      >
        <Text style={styles.floatingAiIcon}>💬</Text>
        <Text style={styles.floatingAiText}>DEVA</Text>
      </Pressable>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: "#F3F4F6",
  },
  scrollContent: {
    padding: 20,
    paddingBottom: 120,
  },
  card: {
    backgroundColor: "#FFFFFF",
    borderRadius: 20,
    padding: 22,
  },
  title: {
    fontSize: 24,
    fontWeight: "800",
    color: "#111827",
    textAlign: "center",
    marginBottom: 14,
  },
  welcome: {
    fontSize: 15,
    color: "#6B7280",
    textAlign: "center",
  },
  name: {
    fontSize: 21,
    color: "#2563EB",
    fontWeight: "800",
    textAlign: "center",
    marginTop: 4,
    marginBottom: 18,
  },
  roleBox: {
    backgroundColor: "#F9FAFB",
    padding: 14,
    borderRadius: 14,
    borderLeftWidth: 5,
    marginBottom: 14,
  },
  roleLabel: {
    color: "#6B7280",
    fontSize: 13,
    marginBottom: 4,
  },
  roleValue: {
    color: "#111827",
    fontSize: 17,
    fontWeight: "800",
  },
  description: {
    fontSize: 15,
    color: "#374151",
    lineHeight: 22,
    marginBottom: 16,
    textAlign: "center",
  },
  motivationCard: {
    backgroundColor: "#FFFBEB",
    borderWidth: 1,
    borderColor: "#F59E0B",
    padding: 14,
    borderRadius: 16,
    marginBottom: 16,
  },
  motivationTitle: {
    fontSize: 16,
    fontWeight: "900",
    color: "#92400E",
    marginBottom: 8,
    textAlign: "center",
  },
  streakText: {
    fontSize: 18,
    fontWeight: "900",
    color: "#111827",
    textAlign: "center",
    marginBottom: 6,
  },
  badgeText: {
    fontSize: 14,
    color: "#374151",
    textAlign: "center",
    marginBottom: 6,
    lineHeight: 20,
  },
  motivationMessage: {
    fontSize: 13,
    color: "#78350F",
    textAlign: "center",
    lineHeight: 19,
  },
  smallRefreshButton: {
    backgroundColor: "#F59E0B",
    padding: 10,
    borderRadius: 10,
    alignItems: "center",
    marginTop: 10,
  },
  smallRefreshText: {
    color: "#FFFFFF",
    fontWeight: "900",
  },
  groupTitle: {
    fontSize: 16,
    fontWeight: "800",
    color: "#111827",
    marginTop: 16,
    marginBottom: 6,
  },
  button: {
    backgroundColor: "#2563EB",
    padding: 14,
    borderRadius: 12,
    alignItems: "center",
    marginTop: 9,
  },
  profileButton: {
    backgroundColor: "#059669",
    padding: 14,
    borderRadius: 12,
    alignItems: "center",
    marginTop: 8,
  },
  messageButton: {
    backgroundColor: "#0F766E",
    padding: 14,
    borderRadius: 12,
    alignItems: "center",
    marginTop: 9,
  },
  riskButton: {
    backgroundColor: "#DC2626",
    padding: 14,
    borderRadius: 12,
    alignItems: "center",
    marginTop: 9,
  },
  notificationButton: {
    backgroundColor: "#F59E0B",
    padding: 14,
    borderRadius: 12,
    alignItems: "center",
    marginTop: 9,
  },
  logoutButton: {
    backgroundColor: "#374151",
    padding: 14,
    borderRadius: 12,
    alignItems: "center",
    marginTop: 18,
  },
  buttonText: {
    color: "#FFFFFF",
    fontSize: 16,
    fontWeight: "800",
  },
  note: {
    color: "#6B7280",
    fontSize: 12,
    lineHeight: 18,
    textAlign: "center",
    marginTop: 18,
  },
  floatingAiButton: {
    position: "absolute",
    right: 22,
    bottom: 28,
    width: 74,
    height: 74,
    borderRadius: 37,
    backgroundColor: "#7C3AED",
    alignItems: "center",
    justifyContent: "center",
    shadowColor: "#000",
    shadowOffset: {
      width: 0,
      height: 4,
    },
    shadowOpacity: 0.25,
    shadowRadius: 8,
    elevation: 8,
  },
  floatingAiIcon: {
    fontSize: 25,
  },
  floatingAiText: {
    color: "#FFFFFF",
    fontSize: 12,
    fontWeight: "900",
    marginTop: 2,
  },
});