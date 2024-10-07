const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

// Function to run shell commands
function runCommand(command) {
  try {
    execSync(command, { stdio: 'inherit' });
  } catch (error) {
    console.error(`Failed to execute command: ${command}`);
    process.exit(1);
  }
}

// Main function
function main() {
  // Ensure we're in the project root
  const packageJsonPath = path.join(process.cwd(), 'package.json');
  if (!fs.existsSync(packageJsonPath)) {
    console.error('package.json not found in the current directory');
    process.exit(1);
  }

  // Generate package-lock.json
  console.log('Generating package-lock.json...');
  runCommand('npm install --package-lock-only');

  // Stage, commit, and push the changes
  console.log('Committing and pushing package-lock.json...');
  runCommand('git config --global user.email "github-actions[bot]@users.noreply.github.com"');
  runCommand('git config --global user.name "github-actions[bot]"');
  runCommand('git add package-lock.json');
  runCommand('git commit -m "Add package-lock.json"');
  runCommand('git push');

  console.log('package-lock.json has been generated and pushed to the repository.');
}

main();
