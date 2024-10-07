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

  // Update packages and generate package-lock.json
  console.log('Updating packages and generating package-lock.json...');
  runCommand('npm update');
  runCommand('npm install');

  // Stage, commit, and push the changes
  console.log('Committing and pushing package-lock.json...');
  runCommand('git config --global user.email "github-actions[bot]@users.noreply.github.com"');
  runCommand('git config --global user.name "github-actions[bot]"');
  runCommand('git add package.json package-lock.json');
  runCommand('git commit -m "Update dependencies and regenerate package-lock.json"');
  runCommand('git push');

  console.log('Dependencies updated and package-lock.json has been regenerated and pushed to the repository.');
}

main();
