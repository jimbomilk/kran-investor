import { expect } from "chai";
import { ethers } from "hardhat";

describe("KranToken", function () {
  it("Should return the correct name and symbol", async function () {
    const KranToken = await ethers.getContractFactory("KranToken");
    const initialSupply = ethers.parseUnits("1000000000", 18);
    const kranToken = await KranToken.deploy(initialSupply);

    expect(await kranToken.name()).to.equal("Kran Token");
    expect(await kranToken.symbol()).to.equal("KRN");
  });

  it("Should have the correct initial supply", async function () {
    const KranToken = await ethers.getContractFactory("KranToken");
    const initialSupply = ethers.parseUnits("1000000000", 18);
    const kranToken = await KranToken.deploy(initialSupply);
    const ownerBalance = await kranToken.balanceOf(await kranToken.runner.getAddress());

    expect(await kranToken.totalSupply()).to.equal(initialSupply);
    expect(ownerBalance).to.equal(initialSupply);
  });
});
