import { ethers } from "hardhat";

async function main() {
  const initialSupply = ethers.parseUnits("1000000000", 18);
  const kranToken = await ethers.deployContract("KranToken", [initialSupply]);

  await kranToken.waitForDeployment();

  console.log(
    `KranToken with initial supply of ${initialSupply} deployed to ${kranToken.target}`
  );
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
