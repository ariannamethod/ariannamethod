package ai.ariannamethod

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.ArrowBack
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.input.PasswordVisualTransformation
import androidx.compose.ui.unit.dp
import androidx.navigation.NavController

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun SettingsView(
    navController: NavController,
    onSave: (String, String, String) -> Unit,
    currentOpenAIKey: String,
    currentAnthropicKey: String,
    currentAMToken: String
) {
    var openaiKey by remember { mutableStateOf(currentOpenAIKey) }
    var anthropicKey by remember { mutableStateOf(currentAnthropicKey) }
    var amToken by remember { mutableStateOf(currentAMToken) }
    var showSaved by remember { mutableStateOf(false) }

    Scaffold(
        topBar = {
            TopAppBar(
                title = {
                    Text(
                        text = "Settings",
                        color = MaterialTheme.colorScheme.onPrimary,
                        style = MaterialTheme.typography.titleLarge
                    )
                },
                navigationIcon = {
                    IconButton(onClick = { navController.popBackStack() }) {
                        Icon(
                            imageVector = Icons.Filled.ArrowBack,
                            contentDescription = "Back",
                            tint = MaterialTheme.colorScheme.onPrimary
                        )
                    }
                },
                colors = TopAppBarDefaults.topAppBarColors(
                    containerColor = MaterialTheme.colorScheme.primary
                )
            )
        }
    ) { paddingValues ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .background(Color.Black)
                .padding(paddingValues)
                .padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(16.dp)
        ) {
            Text(
                text = "API Keys",
                color = Color.White,
                style = MaterialTheme.typography.titleMedium
            )

            Text(
                text = "Enter your API keys. They will be stored securely on your device.",
                color = Color.Gray,
                style = MaterialTheme.typography.bodySmall
            )

            Spacer(modifier = Modifier.height(8.dp))

            // OpenAI API Key
            OutlinedTextField(
                value = openaiKey,
                onValueChange = { openaiKey = it },
                label = { Text("OpenAI API Key") },
                placeholder = { Text("sk-...") },
                visualTransformation = PasswordVisualTransformation(),
                shape = RoundedCornerShape(12.dp),
                colors = TextFieldDefaults.outlinedTextFieldColors(
                    focusedBorderColor = Color.White,
                    unfocusedBorderColor = Color.Gray,
                    cursorColor = Color.White,
                    focusedLabelColor = Color.White,
                    unfocusedLabelColor = Color.Gray,
                    containerColor = Color.Transparent
                ),
                modifier = Modifier.fillMaxWidth()
            )

            // Anthropic API Key
            OutlinedTextField(
                value = anthropicKey,
                onValueChange = { anthropicKey = it },
                label = { Text("Anthropic API Key") },
                placeholder = { Text("sk-ant-...") },
                visualTransformation = PasswordVisualTransformation(),
                shape = RoundedCornerShape(12.dp),
                colors = TextFieldDefaults.outlinedTextFieldColors(
                    focusedBorderColor = Color.White,
                    unfocusedBorderColor = Color.Gray,
                    cursorColor = Color.White,
                    focusedLabelColor = Color.White,
                    unfocusedLabelColor = Color.Gray,
                    containerColor = Color.Transparent
                ),
                modifier = Modifier.fillMaxWidth()
            )

            Spacer(modifier = Modifier.height(16.dp))

            // AMToken (Arianna Method Token) - for Oleg recognition
            OutlinedTextField(
                value = amToken,
                onValueChange = { amToken = it },
                label = { Text("AMToken") },
                placeholder = { Text("Optional: Recognition token") },
                visualTransformation = PasswordVisualTransformation(),
                shape = RoundedCornerShape(12.dp),
                colors = TextFieldDefaults.outlinedTextFieldColors(
                    focusedBorderColor = Color.White,
                    unfocusedBorderColor = Color.Gray,
                    cursorColor = Color.White,
                    focusedLabelColor = Color.White,
                    unfocusedLabelColor = Color.Gray,
                    containerColor = Color.Transparent
                ),
                modifier = Modifier.fillMaxWidth()
            )
            
            Text(
                text = "AMToken is optional. It enables special recognition mode.",
                color = Color.Gray,
                style = MaterialTheme.typography.bodySmall,
                modifier = Modifier.padding(start = 4.dp)
            )

            Spacer(modifier = Modifier.height(16.dp))

            // Save Button
            Button(
                onClick = {
                    onSave(openaiKey, anthropicKey, amToken)
                    showSaved = true
                },
                modifier = Modifier.fillMaxWidth(),
                colors = ButtonDefaults.buttonColors(
                    containerColor = Color.White,
                    contentColor = Color.Black
                ),
                shape = RoundedCornerShape(12.dp)
            ) {
                Text("Save Keys", style = MaterialTheme.typography.titleMedium)
            }

            if (showSaved) {
                LaunchedEffect(Unit) {
                    kotlinx.coroutines.delay(2000)
                    showSaved = false
                    navController.popBackStack()
                }
                Text(
                    text = "✓ Keys saved securely",
                    color = Color.White,
                    modifier = Modifier.align(Alignment.CenterHorizontally)
                )
            }

            Spacer(modifier = Modifier.weight(1f))

            Text(
                text = "Note: Keys are encrypted and stored locally. They never leave your device.",
                color = Color.Gray,
                style = MaterialTheme.typography.bodySmall,
                modifier = Modifier.padding(top = 16.dp)
            )
        }
    }
}

