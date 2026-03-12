        const terminal = document.getElementById('terminal');
        const matrixCanvas = document.getElementById('matrix-canvas');
        let matrixInterval = null;
        const commandHistory = [];
        let historyIndex = -1;
        
        const commands = {
            help: {
                description: "List available commands",
                execute: () => {
                    printOutput("Available commands:");
                    printOutput("  <span style='color:var(--cmd-success)'>help</span>       - Show this help message");
                    printOutput("  <span style='color:var(--cmd-success)'>resume</span>     - View/Download Resume");
                    printOutput("  <span style='color:var(--cmd-success)'>linkedin</span>   - Visit LinkedIn profile");
                    printOutput("  <span style='color:var(--cmd-success)'>sandbox</span>    - Visit Sandbox site (rariai.com)");
                    printOutput("  <span style='color:var(--cmd-success)'>narrative</span>  - View Career Narrative page");
                    printOutput("  <span style='color:var(--cmd-success)'>ls</span>         - List files");
                    printOutput("  <span style='color:var(--cmd-success)'>history</span>    - Show command history");
                    printOutput("  <span style='color:var(--cmd-success)'>clear</span>      - Clear the terminal screen");
                    printOutput("  <span style='color:var(--cmd-success)'>whoami</span>     - Display current user");
                    printOutput("  <span style='color:var(--cmd-success)'>date</span>       - Display current date/time");
                    printOutput("  <span style='color:var(--cmd-success)'>weather</span>    - Check the weather");
                    printOutput("<br>Fun & Utilities:");
                    printOutput("  <span style='color:var(--cmd-success)'>cat [file]</span> - Display file content");
                    printOutput("  <span style='color:var(--cmd-success)'>echo [text]</span> - Echo input text");
                    printOutput("  <span style='color:var(--cmd-success)'>joke</span>       - Tell a random dev joke");
                    printOutput("  <span style='color:var(--cmd-success)'>matrix</span>     - Toggle Matrix rain effect");
                    printOutput("  <span style='color:var(--cmd-success)'>theme [name]</span> - Change theme (default, matrix, light)");
                    printOutput("  <span style='color:var(--cmd-success)'>coffee</span>     - Need caffeine?");
                    printOutput("  <span style='color:var(--cmd-success)'>sudo</span>       - Admin privileges");
                }
            },
            resume: {
                description: "View Resume",
                execute: () => {
                    printOutput("Opening Resume...", "info");
                    window.open('files/Alexander_Ferrara_Resume_11.18.25.pdf', '_blank');
                }
            },
            linkedin: {
                description: "Visit LinkedIn",
                execute: () => {
                    printOutput("Opening LinkedIn...", "info");
                    window.open('https://www.linkedin.com/in/a-ferrara/', '_blank');
                }
            },
            sandbox: {
                description: "Visit Sandbox",
                execute: () => {
                    printOutput("Opening Sandbox...", "info");
                    window.open('https://www.alexanderferrara.com/legacy/RARIAI/', '_blank');
                }
            },
            narrative: {
                description: "View Career Narrative",
                execute: () => {
                    printOutput("Opening Career Narrative...", "info");
                    window.location.href = 'career-narrative/';
                }
            },
            ls: {
                description: "List files",
                execute: () => {
                    printOutput("resume.pdf  linkedin.url  sandbox.url  narrative.dir  blog.dir  legacy.dir  index.html  secret.txt");
                }
            },
            history: {
                description: "History",
                execute: () => {
                    commandHistory.forEach((cmd, i) => {
                        printOutput(`${i + 1}  ${cmd}`);
                    });
                }
            },
            clear: {
                description: "Clear screen",
                execute: () => {
                    terminal.innerHTML = '';
                    createNewInputLine();
                    return true;
                }
            },
            whoami: {
                description: "Current user",
                execute: () => {
                    printOutput("visitor");
                }
            },
            date: {
                description: "Display date",
                execute: () => {
                    printOutput(new Date().toString());
                }
            },
            echo: {
                description: "Echo input",
                execute: (args) => {
                    printOutput(args || "");
                }
            },
            weather: {
                description: "Current weather",
                execute: () => {
                    const weathers = [
                        "Sunny, 72°F. Perfect day for coding.",
                        "Cloudy with a chance of merge conflicts.",
                        "Rainy. Good time to stay inside and hack.",
                        "404 Weather Not Found."
                    ];
                    printOutput(weathers[Math.floor(Math.random() * weathers.length)]);
                }
            },
            // joke: {
            //     description: "Tell a joke",
            //     execute: () => {
            //         const jokes = [
            //             "Why do programmers prefer dark mode? Because light attracts bugs.",
            //             "How many programmers does it take to change a light bulb? None, that's a hardware problem.",
            //             "I would tell you a UDP joke, but you might not get it.",
            //             "A SQL query walks into a bar, walks up to two tables and asks, 'Can I join you?'",
            //             "There are 10 types of people in the world: those who understand binary, and those who don't."
            //         ];
            //         printOutput(jokes[Math.floor(Math.random() * jokes.length)]);
            //     }
            // },
            // Fun Commands
            sudo: {
                description: "Admin",
                execute: () => {
                    printOutput("visitor is not in the sudoers file. This incident will be reported.", "error");
                }
            },
            rm: {
                description: "Remove file",
                execute: (args) => {
                    if (args.includes("-rf") && args.includes("/")) {
                        printOutput("I'm sorry, Dave. I'm afraid I can't do that.", "error");
                    } else {
                        printOutput("Permission denied.", "error");
                    }
                }
            },
            vi: {
                description: "Editor",
                execute: () => {
                    printOutput("You are now trapped in VIM. Refresh page to exit.", "info");
                }
            },
            vim: {
                description: "Editor",
                execute: () => {
                    printOutput("You are now trapped in VIM. Refresh page to exit.", "info");
                }
            },
            cat: {
                description: "Concatenate files",
                execute: (args) => {
                    if (!args) {
                        printOutput("Usage: cat [file]");
                        return;
                    }
                    if (args.includes("resume")) {
                        printOutput("&lt;TODO Placeholder: Plaintext resume will go here.&gt;", "info");
                    } else if (args.includes("secret.txt")) {
                        printOutput("42");
                    } else if (args.includes("index.html")) {
                        printOutput("Wait, that's recursion!");
                    } else {
                        printOutput(`cat: ${args}: No such file or directory`, "error");
                    }
                }
            },
            coffee: {
                description: "Coffee",
                execute: () => {
                    printOutput(`
    (  )   (   )  )
     ) (   )  (  (
     ( )  (    ) )
     _____________
    <_____________> ___
    |             |/ _ \\
    |               | | |
    |               |_| |
    |             |\\___/
    \\_____________/_/
                    `, "info");
                }
            },
            matrix: {
                description: "Matrix Effect",
                execute: () => {
                    if (matrixInterval) {
                        clearInterval(matrixInterval);
                        matrixInterval = null;
                        matrixCanvas.style.display = 'none';
                        document.body.classList.remove('theme-matrix');
                        printOutput("Matrix mode deactivated.", "info");
                    } else {
                        matrixCanvas.style.display = 'block';
                        startMatrix();
                        document.body.classList.add('theme-matrix');
                        printOutput("Follow the white rabbit...", "success");
                    }
                }
            },
            theme: {
                description: "Change Theme",
                execute: (args) => {
                    if (!args) {
                        printOutput("Usage: theme [default|matrix|light]");
                        return;
                    }
                    const theme = args.trim().toLowerCase();
                    document.body.className = ""; // Reset
                    if (theme === 'matrix') {
                        document.body.classList.add('theme-matrix');
                        // Ensure matrix effect is on? Maybe just style.
                        printOutput("Theme set to Matrix.", "success");
                    } else if (theme === 'light') {
                        document.body.classList.add('theme-light');
                        printOutput("Theme set to Light. My eyes!", "info");
                    } else if (theme === 'default') {
                        printOutput("Theme set to Default.", "success");
                    } else {
                        printOutput(`Unknown theme: ${theme}`, "error");
                    }
                }
            }
        };

        // Matrix Effect Logic
        function startMatrix() {
            const ctx = matrixCanvas.getContext('2d');
            matrixCanvas.width = window.innerWidth;
            matrixCanvas.height = window.innerHeight;

            const katakana = 'アァカサタナハマヤャラワガザダバパイィキシチニヒミリヰギジヂビピウゥクスツヌフムユュルグズブヅプエェケセテネヘメレヱゲゼデベペオォコソトノホモヨョロヲゴゾドボポヴッン';
            const latin = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ';
            const nums = '0123456789';
            const alphabet = katakana + latin + nums;

            const fontSize = 16;
            const columns = matrixCanvas.width/fontSize;
            const drops = [];

            for(let x = 0; x < columns; x++) {
                drops[x] = 1;
            }

            const draw = () => {
                ctx.fillStyle = 'rgba(0, 0, 0, 0.05)';
                ctx.fillRect(0, 0, matrixCanvas.width, matrixCanvas.height);

                ctx.fillStyle = '#0F0';
                ctx.font = fontSize + 'px monospace';

                for(let i = 0; i < drops.length; i++) {
                    const text = alphabet.charAt(Math.floor(Math.random() * alphabet.length));
                    ctx.fillText(text, i*fontSize, drops[i]*fontSize);

                    if(drops[i]*fontSize > matrixCanvas.height && Math.random() > 0.975)
                        drops[i] = 0;
                    
                    drops[i]++;
                }
            };

            matrixInterval = setInterval(draw, 30);
        }

        // P10k Prompt HTML generator
        function getPromptHTML() {
            return `
            <div class="p10k-prompt">
                <span class="segment seg-user"><i class="fa fa-user"></i> visitor</span>
                <span class="segment seg-dir"><i class="fa fa-folder-open"></i> ~</span>
            </div>`;
        }

        function createNewInputLine(initialValue = '') {
            const line = document.createElement('div');
            line.className = 'command-line';
            line.innerHTML = getPromptHTML() + `<input type="text" id="input" autocomplete="off" autofocus spellcheck="false" value="${initialValue}">`;
            terminal.appendChild(line);
            
            const input = line.querySelector('#input');
            input.focus();
            // Move cursor to end
            const len = input.value.length;
            input.setSelectionRange(len, len);
            
            // Reset history index when starting new line
            historyIndex = -1;

            input.addEventListener('keydown', (e) => {
                if (e.key === 'Enter') {
                    const cmd = input.value;
                    input.disabled = true; // Disable old input
                    
                    if (cmd.trim() !== '') {
                        commandHistory.push(cmd);
                    }
                    
                    processCommand(cmd);
                } else if (e.key === 'Tab') {
                    e.preventDefault(); // Prevent focus loss
                    
                    const currentVal = input.value;
                    // Only autocomplete if we are typing the command (first word)
                    // If there's a space, we might be typing args, which we don't support yet
                    if (currentVal.indexOf(' ') === -1) {
                        const partialCmd = currentVal.toLowerCase();
                        const matches = Object.keys(commands).filter(cmd => cmd.startsWith(partialCmd));
                        
                        if (matches.length === 1) {
                            input.value = matches[0] + ' '; // Complete and add space
                        } else if (matches.length > 1) {
                            // Show ambiguous matches
                            // We need to disable current input, print matches, then create new input line with same content
                            input.disabled = true;
                            
                            // Print the matches below the CURRENT prompt
                            const matchesDiv = document.createElement('div');
                            matchesDiv.className = 'output';
                            matchesDiv.style.color = "var(--link-color)";
                            matchesDiv.textContent = matches.join('  ');
                            terminal.appendChild(matchesDiv);
                            
                            // Create NEW input line with same content
                            createNewInputLine(currentVal);
                        }
                    }
                } else if (e.key === 'ArrowUp') {
                    e.preventDefault();
                    if (commandHistory.length > 0) {
                        if (historyIndex === -1) {
                            historyIndex = commandHistory.length - 1;
                        } else if (historyIndex > 0) {
                            historyIndex--;
                        }
                        input.value = commandHistory[historyIndex];
                        // Move cursor to end
                        setTimeout(() => input.setSelectionRange(input.value.length, input.value.length), 0);
                    }
                } else if (e.key === 'ArrowDown') {
                    e.preventDefault();
                    if (historyIndex !== -1) {
                        if (historyIndex < commandHistory.length - 1) {
                            historyIndex++;
                            input.value = commandHistory[historyIndex];
                        } else {
                            historyIndex = -1;
                            input.value = '';
                        }
                        // Move cursor to end
                        setTimeout(() => input.setSelectionRange(input.value.length, input.value.length), 0);
                    }
                }
            });
            
            // Scroll to bottom
            terminal.scrollTop = terminal.scrollHeight;
        }
        
        function focusInput() {
            const input = document.querySelector('#input:not([disabled])');
            if (input) input.focus();
        }

        function printOutput(text, type="normal") {
            const div = document.createElement('div');
            div.className = 'output command-result';
            if (type === "info") div.style.color = "var(--link-color)";
            if (type === "success") div.style.color = "var(--cmd-success)";
            if (type === "error") div.style.color = "var(--cmd-error)";
            div.innerHTML = text;
            terminal.appendChild(div);
            terminal.scrollTop = terminal.scrollHeight;
        }

        function processCommand(cmd) {
            const cleanCmd = cmd.trim();
            
            if (cleanCmd !== '') {
                const parts = cleanCmd.split(' ');
                const cmdKey = parts[0].toLowerCase();
                const args = parts.slice(1).join(' '); // Simple arg joining
                
                if (commands[cmdKey]) {
                    const cleared = commands[cmdKey].execute(args);
                    if (cleared) return; // Don't create new line if cleared
                } else {
                    printOutput(`<span style='color:var(--cmd-error)'>Command not found:</span> ${cleanCmd}. Type <span style='color:var(--cmd-success)'>help</span> for available commands.`);
                }
            }
            
            createNewInputLine();
        }

        function toggleDropdown(id) {
            const el = document.getElementById(id);
            el.classList.toggle('show');
        }

        function handleMenuClick(cmd) {
            const activeInput = document.querySelector('#input:not([disabled])');
            if (activeInput) {
                activeInput.value = cmd;
                activeInput.disabled = true;
                processCommand(cmd);
            }
            // Close dropdown
            document.getElementById('file-dropdown').classList.remove('show');
        }

        // Close dropdown if clicked outside
        window.onclick = function(event) {
            if (!event.target.matches('.menu-item') && !event.target.closest('.menu-dropdown')) {
                const dd = document.getElementById('file-dropdown');
                if (dd.classList.contains('show')) {
                    dd.classList.remove('show');
                }
            }
        }
        
        // Handle window resize for matrix
        window.addEventListener('resize', () => {
            if(matrixInterval) {
                clearInterval(matrixInterval);
                startMatrix();
            }
        });

        // Initialize
        createNewInputLine();