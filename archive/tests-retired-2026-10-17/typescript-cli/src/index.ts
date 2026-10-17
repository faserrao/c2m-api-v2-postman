import yargs from 'yargs';
import { hideBin } from 'yargs/helpers';
import axios from 'axios';
import dotenv from 'dotenv';

dotenv.config();

const argv = yargs(hideBin(process.argv))
  .option('env', { type: 'string', default: 'dev', choices: ['dev', 'staging', 'production'], describe: 'Target environment' })
  .option('token', { type: 'string', describe: 'JWT token override' })
  .option('dryRun', { type: 'boolean', default: false, describe: 'Print config without making requests' })
  .argv;

const BASE_URLS: Record<string, string> = {
  dev: 'https://dev.api.example.com',
  staging: 'https://staging.api.example.com',
  production: 'https://api.example.com'
};

(async () => {
  const baseUrl = BASE_URLS[argv.env];
  const token = argv.token || process.env.TOKEN;

  if (!token) {
    console.error('❌ Missing JWT token. Pass --token or set TOKEN in .env.');
    process.exit(1);
  }

  const request = {
    method: 'post',
    url: `${baseUrl}/jobs/submit/single/doc`,
    headers: {
      Authorization: `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    data: {
      documentSourceIdentifier: { documentId: "doc_123" },
      recipientAddresses: [{ addressId: "addr_456" }],
      jobOptions: {
        documentClass: "businessLetter",
        layout: "portrait",
        mailclass: "firstClassMail",
        paperType: "letter",
        printOption: "color",
        envelope: "flat"
      }
    }
  };

  if (argv.dryRun) {
    console.log("🔧 Dry run config:", JSON.stringify(request, null, 2));
    return;
  }

  try {
    const res = await axios(request);
    console.log("✅ Success:", res.data);
  } catch (err: any) {
    console.error("❌ Request failed:", err.response?.data || err.message);
  }
})();