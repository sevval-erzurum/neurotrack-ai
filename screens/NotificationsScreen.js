import { useEffect, useState } from "react";
import {
  Alert,
  Pressable,
  SafeAreaView,
  ScrollView,
  StyleSheet,
  Text,
  View,
} from "react-native";

import {
  getSmartNotifications,
  markNotificationRead,
} from "../services/api";

export default function NotificationsScreen({ user, onBack }) {
  const [notifications, setNotifications] = useState([]);

  async function loadNotifications() {
    try {
      const { response, data } = await getSmartNotifications(user.user_id);

      if (response.ok) {
        setNotifications(data);
      } else {
        Alert.alert("Bildirim hatası", JSON.stringify(data));
      }
    } catch (error) {
      Alert.alert("Bağlantı hatası", String(error));
    }
  }

  async function handleMarkRead(notificationId) {
    try {
      const { response, data } = await markNotificationRead(notificationId);

      if (response.ok) {
        loadNotifications();
      } else {
        Alert.alert("İşlem hatası", JSON.stringify(data));
      }
    } catch (error) {
      Alert.alert("Bağlantı hatası", String(error));
    }
  }

  function getCardStyle(title, isRead) {
    if (isRead) return styles.readCard;

    if (title.includes("mesaj")) return styles.messageCard;
    if (title.includes("sohbet")) return styles.messageCard;
    if (title.includes("günlük")) return styles.warningCard;
    if (title.includes("görüşme")) return styles.appointmentCard;

    return styles.unreadCard;
  }

  useEffect(() => {
    loadNotifications();
  }, []);

  const unreadCount = notifications.filter((item) => !item.is_read).length;

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView>
        <Text style={styles.title}>Bildirimlerim</Text>

        <View style={styles.summaryBox}>
          <Text style={styles.summaryTitle}>Bildirim Özeti</Text>
          <Text style={styles.summaryText}>
            Toplam bildirim: {notifications.length}
          </Text>
          <Text style={styles.summaryText}>
            Okunmamış bildirim: {unreadCount}
          </Text>
        </View>

        <Pressable style={styles.refreshButton} onPress={loadNotifications}>
          <Text style={styles.buttonText}>Bildirimleri Yenile</Text>
        </Pressable>

        {notifications.length === 0 ? (
          <View style={styles.emptyBox}>
            <Text style={styles.emptyText}>Henüz bildirim yok.</Text>
          </View>
        ) : (
          notifications.map((item) => (
            <View
              key={item.id}
              style={getCardStyle(item.title, item.is_read)}
            >
              <View style={styles.cardHeader}>
                <Text style={styles.cardTitle}>{item.title}</Text>

                {!item.is_read && (
                  <View style={styles.badge}>
                    <Text style={styles.badgeText}>Yeni</Text>
                  </View>
                )}
              </View>

              <Text style={styles.cardMessage}>{item.message}</Text>

              <Text style={styles.dateText}>
                Tarih: {item.created_at || "-"}
              </Text>

              {!item.is_read && (
                <Pressable
                  style={styles.smallButton}
                  onPress={() => handleMarkRead(item.id)}
                >
                  <Text style={styles.smallButtonText}>Okundu İşaretle</Text>
                </Pressable>
              )}
            </View>
          ))
        )}

        <Pressable style={styles.backButton} onPress={onBack}>
          <Text style={styles.buttonText}>Ana Sayfaya Dön</Text>
        </Pressable>
      </ScrollView>
    </SafeAreaView>
  );
}

const baseCard = {
  padding: 16,
  borderRadius: 16,
  marginBottom: 12,
  borderWidth: 1,
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: "#F3F4F6",
    padding: 20,
  },
  title: {
    fontSize: 24,
    fontWeight: "900",
    color: "#111827",
    marginBottom: 16,
    textAlign: "center",
  },
  summaryBox: {
    backgroundColor: "#FFFFFF",
    padding: 16,
    borderRadius: 16,
    marginBottom: 14,
  },
  summaryTitle: {
    fontSize: 18,
    fontWeight: "900",
    color: "#111827",
    marginBottom: 6,
  },
  summaryText: {
    fontSize: 14,
    color: "#374151",
    marginBottom: 4,
  },
  unreadCard: {
    ...baseCard,
    backgroundColor: "#FEF3C7",
    borderColor: "#F59E0B",
  },
  readCard: {
    ...baseCard,
    backgroundColor: "#FFFFFF",
    borderColor: "#E5E7EB",
  },
  messageCard: {
    ...baseCard,
    backgroundColor: "#DBEAFE",
    borderColor: "#2563EB",
  },
  warningCard: {
    ...baseCard,
    backgroundColor: "#FEF3C7",
    borderColor: "#F59E0B",
  },
  appointmentCard: {
    ...baseCard,
    backgroundColor: "#F5F3FF",
    borderColor: "#7C3AED",
  },
  cardHeader: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: 6,
  },
  cardTitle: {
    fontSize: 17,
    fontWeight: "900",
    color: "#111827",
    flex: 1,
  },
  badge: {
    backgroundColor: "#DC2626",
    paddingVertical: 4,
    paddingHorizontal: 8,
    borderRadius: 999,
    marginLeft: 8,
  },
  badgeText: {
    color: "#FFFFFF",
    fontSize: 11,
    fontWeight: "900",
  },
  cardMessage: {
    fontSize: 15,
    color: "#374151",
    lineHeight: 21,
    marginBottom: 8,
  },
  dateText: {
    fontSize: 12,
    color: "#6B7280",
    marginBottom: 8,
  },
  smallButton: {
    backgroundColor: "#2563EB",
    padding: 10,
    borderRadius: 10,
    alignItems: "center",
  },
  smallButtonText: {
    color: "#FFFFFF",
    fontWeight: "900",
  },
  refreshButton: {
    backgroundColor: "#059669",
    padding: 14,
    borderRadius: 12,
    alignItems: "center",
    marginBottom: 14,
  },
  backButton: {
    backgroundColor: "#374151",
    padding: 14,
    borderRadius: 12,
    alignItems: "center",
    marginTop: 18,
    marginBottom: 24,
  },
  buttonText: {
    color: "#FFFFFF",
    fontSize: 16,
    fontWeight: "900",
  },
  emptyBox: {
    backgroundColor: "#FFFFFF",
    padding: 18,
    borderRadius: 16,
    marginTop: 10,
  },
  emptyText: {
    color: "#6B7280",
    textAlign: "center",
  },
});