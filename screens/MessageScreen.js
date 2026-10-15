import { useEffect, useState } from "react";
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

import {
    getAvailableDoctorsForMessage,
    getMessageContacts,
    getMessageRequests,
    respondMessageRequest,
    secureConversation,
    secureSendMessage,
    sendMessageRequest,
} from "../services/api";

export default function MessageScreen({ user, onBack }) {
  const [availableDoctors, setAvailableDoctors] = useState([]);
  const [requests, setRequests] = useState([]);
  const [contacts, setContacts] = useState([]);

  const [selectedUser, setSelectedUser] = useState(null);
  const [conversationMessages, setConversationMessages] = useState([]);
  const [messageText, setMessageText] = useState("");

  async function loadAll() {
    await loadAvailableDoctors();
    await loadRequests();
    await loadContacts();
  }

  async function loadAvailableDoctors() {
    try {
      const { response, data } = await getAvailableDoctorsForMessage(user.user_id);

      if (response.ok) {
        setAvailableDoctors(data);
      }
    } catch (error) {
      Alert.alert("Bağlantı hatası", String(error));
    }
  }

  async function loadRequests() {
    try {
      const { response, data } = await getMessageRequests(user.user_id);

      if (response.ok) {
        setRequests(data);
      } else {
        Alert.alert("İstek listeleme hatası", JSON.stringify(data));
      }
    } catch (error) {
      Alert.alert("Bağlantı hatası", String(error));
    }
  }

  async function loadContacts() {
    try {
      const { response, data } = await getMessageContacts(user.user_id);

      if (response.ok) {
        setContacts(data);
      } else {
        Alert.alert("Konuşma listeleme hatası", JSON.stringify(data));
      }
    } catch (error) {
      Alert.alert("Bağlantı hatası", String(error));
    }
  }

  async function handleSendRequest(doctorId) {
    try {
      const { response, data } = await sendMessageRequest(user.user_id, doctorId);

      if (response.ok) {
        Alert.alert("Başarılı", data.message || "Mesaj isteği gönderildi.");
        loadAll();
      } else {
        Alert.alert("İstek hatası", data.detail ? String(data.detail) : JSON.stringify(data));
      }
    } catch (error) {
      Alert.alert("Bağlantı hatası", String(error));
    }
  }

  async function handleRespondRequest(requestId, status) {
    try {
      const { response, data } = await respondMessageRequest(
        requestId,
        status,
        user.user_id
      );

      if (response.ok) {
        Alert.alert("Başarılı", data.message || "İstek güncellendi.");
        loadAll();
      } else {
        Alert.alert("İstek cevaplama hatası", data.detail ? String(data.detail) : JSON.stringify(data));
      }
    } catch (error) {
      Alert.alert("Bağlantı hatası", String(error));
    }
  }

  async function openConversation(contact) {
    setSelectedUser(contact);

    try {
      const { response, data } = await secureConversation(
        user.user_id,
        contact.user_id
      );

      if (response.ok) {
        setConversationMessages(data);
      } else {
        Alert.alert("Konuşma hatası", data.detail ? String(data.detail) : JSON.stringify(data));
      }
    } catch (error) {
      Alert.alert("Bağlantı hatası", String(error));
    }
  }

  async function handleSendMessage() {
    if (!selectedUser) {
      Alert.alert("Hata", "Önce konuşma seç.");
      return;
    }

    if (!messageText.trim()) {
      Alert.alert("Eksik mesaj", "Mesaj boş olamaz.");
      return;
    }

    try {
      const { response, data } = await secureSendMessage(
        user.user_id,
        selectedUser.user_id,
        messageText
      );

      if (response.ok) {
        setMessageText("");
        await openConversation(selectedUser);
        await loadContacts();
      } else {
        Alert.alert("Mesaj hatası", data.detail ? String(data.detail) : JSON.stringify(data));
      }
    } catch (error) {
      Alert.alert("Bağlantı hatası", String(error));
    }
  }

  useEffect(() => {
    loadAll();
  }, []);

  if (selectedUser) {
    return (
      <SafeAreaView style={styles.container}>
        <View style={styles.chatHeader}>
          <View>
            <Text style={styles.chatTitle}>{selectedUser.full_name}</Text>
            <Text style={styles.chatSubtitle}>
              ID: {selectedUser.user_id} / Rol: {selectedUser.role}
            </Text>
          </View>

          <Pressable
            style={styles.headerBackButton}
            onPress={() => {
              setSelectedUser(null);
              setConversationMessages([]);
              loadAll();
            }}
          >
            <Text style={styles.headerBackText}>Geri</Text>
          </Pressable>
        </View>

        <ScrollView style={styles.chatArea}>
          {conversationMessages.length === 0 ? (
            <Text style={styles.emptyText}>Henüz mesaj yok.</Text>
          ) : (
            conversationMessages.map((msg) => {
              const isMine = msg.sender_id === user.user_id;

              return (
                <View
                  key={msg.id}
                  style={isMine ? styles.myBubble : styles.otherBubble}
                >
                  <Text style={styles.bubbleSender}>
                    {isMine ? "Sen" : msg.sender_name}
                  </Text>

                  <Text style={styles.bubbleText}>{msg.content}</Text>

                  <Text style={styles.bubbleDate}>
                    {msg.created_at || "-"}
                  </Text>
                </View>
              );
            })
          )}
        </ScrollView>

        <View style={styles.messageInputArea}>
          <TextInput
            placeholder="Mesaj yaz..."
            placeholderTextColor="#6B7280"
            value={messageText}
            onChangeText={setMessageText}
            style={styles.messageInput}
            multiline
          />

          <Pressable style={styles.sendButton} onPress={handleSendMessage}>
            <Text style={styles.sendButtonText}>Gönder</Text>
          </Pressable>
        </View>
      </SafeAreaView>
    );
  }

  const incomingPendingRequests = requests.filter(
    (item) => item.receiver_id === user.user_id && item.status === "pending"
  );

  const outgoingRequests = requests.filter(
    (item) => item.sender_id === user.user_id
  );

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView>
        <Text style={styles.title}>
          {user.role === "doctor" ? "Hasta Mesajları" : "Doktor Mesajları"}
        </Text>

        <View style={styles.infoBox}>
          <Text style={styles.infoText}>Senin kullanıcı ID: {user.user_id}</Text>
          <Text style={styles.infoText}>
            Sohbet yalnızca atanmış doktor-hasta ilişkisi ve kabul edilen mesaj isteği ile açılır.
          </Text>
        </View>

        {user.role !== "doctor" && (
          <>
            <Text style={styles.sectionTitle}>Doktorlarım</Text>

            {availableDoctors.length === 0 ? (
              <Text style={styles.emptyText}>
                Mesajlaşabileceğin atanmış doktor bulunamadı.
              </Text>
            ) : (
              availableDoctors.map((doctor) => (
                <View key={doctor.user_id} style={styles.doctorCard}>
                  <Text style={styles.cardTitle}>{doctor.full_name}</Text>
                  <Text style={styles.smallText}>ID: {doctor.user_id}</Text>
                  <Text style={styles.smallText}>Email: {doctor.email}</Text>
                  <Text style={styles.statusText}>
                    İstek Durumu: {doctor.request_status}
                  </Text>

                  {doctor.request_status === "none" && (
                    <Pressable
                      style={styles.requestButton}
                      onPress={() => handleSendRequest(doctor.user_id)}
                    >
                      <Text style={styles.buttonText}>Sohbet İsteği Gönder</Text>
                    </Pressable>
                  )}

                  {doctor.request_status === "pending" && (
                    <View style={styles.pendingBox}>
                      <Text style={styles.pendingText}>Doktor onayı bekleniyor.</Text>
                    </View>
                  )}

                  {doctor.request_status === "accepted" && (
                    <View style={styles.acceptedBox}>
                      <Text style={styles.acceptedText}>Sohbet onaylandı.</Text>
                    </View>
                  )}
                </View>
              ))
            )}

            <Text style={styles.sectionTitle}>Gönderdiğim İstekler</Text>

            {outgoingRequests.length === 0 ? (
              <Text style={styles.emptyText}>Henüz mesaj isteği göndermedin.</Text>
            ) : (
              outgoingRequests.map((req) => (
                <View key={req.id} style={styles.requestCard}>
                  <Text style={styles.cardTitle}>{req.receiver_name}</Text>
                  <Text style={styles.smallText}>Doktor ID: {req.receiver_id}</Text>
                  <Text style={styles.statusText}>Durum: {req.status}</Text>
                </View>
              ))
            )}
          </>
        )}

        {user.role === "doctor" && (
          <>
            <Text style={styles.sectionTitle}>Bekleyen Mesaj İstekleri</Text>

            {incomingPendingRequests.length === 0 ? (
              <Text style={styles.emptyText}>Bekleyen istek yok.</Text>
            ) : (
              incomingPendingRequests.map((req) => (
                <View key={req.id} style={styles.requestCard}>
                  <Text style={styles.cardTitle}>{req.sender_name}</Text>
                  <Text style={styles.smallText}>Hasta ID: {req.sender_id}</Text>
                  <Text style={styles.smallText}>Rol: {req.sender_role}</Text>

                  <View style={styles.row}>
                    <Pressable
                      style={styles.acceptButton}
                      onPress={() => handleRespondRequest(req.id, "accepted")}
                    >
                      <Text style={styles.buttonText}>Kabul Et</Text>
                    </Pressable>

                    <Pressable
                      style={styles.rejectButton}
                      onPress={() => handleRespondRequest(req.id, "rejected")}
                    >
                      <Text style={styles.buttonText}>Reddet</Text>
                    </Pressable>
                  </View>
                </View>
              ))
            )}
          </>
        )}

        <Text style={styles.sectionTitle}>Onaylı Konuşmalar</Text>

        <Pressable style={styles.refreshButton} onPress={loadAll}>
          <Text style={styles.buttonText}>Yenile</Text>
        </Pressable>

        {contacts.length === 0 ? (
          <Text style={styles.emptyText}>Henüz onaylı konuşma yok.</Text>
        ) : (
          contacts.map((contact) => (
            <Pressable
              key={contact.user_id}
              style={styles.conversationCard}
              onPress={() => openConversation(contact)}
            >
              <Text style={styles.conversationName}>{contact.full_name}</Text>
              <Text style={styles.smallText}>
                ID: {contact.user_id} / Rol: {contact.role}
              </Text>
              <Text style={styles.lastMessage}>{contact.last_message}</Text>
              <Text style={styles.dateText}>{contact.last_date || "-"}</Text>
            </Pressable>
          ))
        )}

        <Pressable style={styles.backButton} onPress={onBack}>
          <Text style={styles.buttonText}>Ana Sayfaya Dön</Text>
        </Pressable>
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: "#F3F4F6",
    padding: 18,
  },
  title: {
    fontSize: 24,
    fontWeight: "900",
    color: "#111827",
    textAlign: "center",
    marginBottom: 14,
  },
  infoBox: {
    backgroundColor: "#EFF6FF",
    padding: 14,
    borderRadius: 14,
    marginBottom: 14,
  },
  infoText: {
    color: "#2563EB",
    fontSize: 13,
    lineHeight: 20,
    fontWeight: "700",
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: "900",
    color: "#111827",
    marginTop: 16,
    marginBottom: 10,
  },
  doctorCard: {
    backgroundColor: "#FFFFFF",
    padding: 15,
    borderRadius: 16,
    marginBottom: 10,
  },
  requestCard: {
    backgroundColor: "#FFFFFF",
    padding: 15,
    borderRadius: 16,
    marginBottom: 10,
  },
  conversationCard: {
    backgroundColor: "#FFFFFF",
    padding: 15,
    borderRadius: 16,
    marginBottom: 10,
  },
  cardTitle: {
    fontSize: 17,
    fontWeight: "900",
    color: "#111827",
    marginBottom: 4,
  },
  smallText: {
    fontSize: 13,
    color: "#374151",
    marginBottom: 3,
  },
  statusText: {
    fontSize: 13,
    color: "#7C3AED",
    fontWeight: "800",
    marginTop: 4,
    marginBottom: 8,
  },
  requestButton: {
    backgroundColor: "#2563EB",
    padding: 12,
    borderRadius: 12,
    alignItems: "center",
    marginTop: 8,
  },
  pendingBox: {
    backgroundColor: "#FEF3C7",
    padding: 10,
    borderRadius: 10,
    marginTop: 8,
  },
  pendingText: {
    color: "#92400E",
    fontWeight: "800",
    textAlign: "center",
  },
  acceptedBox: {
    backgroundColor: "#DCFCE7",
    padding: 10,
    borderRadius: 10,
    marginTop: 8,
  },
  acceptedText: {
    color: "#166534",
    fontWeight: "800",
    textAlign: "center",
  },
  row: {
    flexDirection: "row",
    gap: 8,
    marginTop: 8,
  },
  acceptButton: {
    flex: 1,
    backgroundColor: "#059669",
    padding: 12,
    borderRadius: 12,
    alignItems: "center",
  },
  rejectButton: {
    flex: 1,
    backgroundColor: "#DC2626",
    padding: 12,
    borderRadius: 12,
    alignItems: "center",
  },
  refreshButton: {
    backgroundColor: "#059669",
    padding: 13,
    borderRadius: 12,
    alignItems: "center",
    marginBottom: 12,
  },
  conversationName: {
    fontSize: 17,
    fontWeight: "900",
    color: "#111827",
  },
  lastMessage: {
    fontSize: 14,
    color: "#374151",
    lineHeight: 20,
    marginTop: 6,
    marginBottom: 6,
  },
  dateText: {
    fontSize: 11,
    color: "#6B7280",
  },
  chatHeader: {
    backgroundColor: "#FFFFFF",
    padding: 14,
    borderRadius: 16,
    marginBottom: 12,
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
  },
  chatTitle: {
    fontSize: 18,
    fontWeight: "900",
    color: "#111827",
  },
  chatSubtitle: {
    fontSize: 12,
    color: "#6B7280",
    marginTop: 2,
  },
  headerBackButton: {
    backgroundColor: "#374151",
    paddingVertical: 9,
    paddingHorizontal: 13,
    borderRadius: 10,
  },
  headerBackText: {
    color: "#FFFFFF",
    fontWeight: "800",
  },
  chatArea: {
    flex: 1,
    backgroundColor: "#FFFFFF",
    borderRadius: 16,
    padding: 12,
    marginBottom: 12,
  },
  myBubble: {
    alignSelf: "flex-end",
    backgroundColor: "#DBEAFE",
    padding: 12,
    borderRadius: 16,
    marginBottom: 10,
    maxWidth: "82%",
  },
  otherBubble: {
    alignSelf: "flex-start",
    backgroundColor: "#DCFCE7",
    padding: 12,
    borderRadius: 16,
    marginBottom: 10,
    maxWidth: "82%",
  },
  bubbleSender: {
    fontSize: 12,
    fontWeight: "900",
    color: "#374151",
    marginBottom: 5,
  },
  bubbleText: {
    fontSize: 15,
    color: "#111827",
    lineHeight: 21,
  },
  bubbleDate: {
    fontSize: 10,
    color: "#6B7280",
    marginTop: 6,
    textAlign: "right",
  },
  messageInputArea: {
    backgroundColor: "#FFFFFF",
    padding: 10,
    borderRadius: 16,
    flexDirection: "row",
    gap: 8,
    alignItems: "flex-end",
  },
  messageInput: {
    flex: 1,
    borderWidth: 1,
    borderColor: "#CBD5E1",
    borderRadius: 12,
    padding: 11,
    minHeight: 44,
    maxHeight: 100,
    color: "#111827",
  },
  sendButton: {
    backgroundColor: "#2563EB",
    paddingVertical: 13,
    paddingHorizontal: 14,
    borderRadius: 12,
  },
  sendButtonText: {
    color: "#FFFFFF",
    fontWeight: "900",
  },
  emptyText: {
    color: "#6B7280",
    textAlign: "center",
    marginTop: 10,
    marginBottom: 12,
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
});