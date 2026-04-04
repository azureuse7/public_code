# Amazon EBS

## What is Amazon EBS?

**Amazon Elastic Block Store (EBS)** is a scalable, high-performance block storage service provided by Amazon Web Services (AWS). It is designed to be used with Amazon Elastic Compute Cloud (EC2) instances, providing persistent storage that can be attached to your virtual machines (instances) in the AWS cloud.

## Key Features of Amazon EBS

1. **Persistent Storage:** Unlike the ephemeral storage that comes with EC2 instances, EBS volumes persist independently of the life of an instance. This means data remains intact even if the instance is stopped or terminated.
2. **Scalability:** EBS allows you to easily scale storage up or down based on your needs without disrupting applications.
3. **Performance Options:**
   - **General Purpose SSD (gp3):** Balanced price and performance for a wide variety of workloads.
   - **Provisioned IOPS SSD (io2):** High performance for mission-critical applications requiring sustained IOPS performance.
   - **Throughput Optimized HDD (st1):** Low-cost HDD storage for frequently accessed, throughput-intensive workloads.
   - **Cold HDD (sc1):** Lowest cost HDD storage for less frequently accessed data.
4. **Snapshot and Backup:** You can create point-in-time snapshots of your EBS volumes, which are stored in Amazon S3. These snapshots can be used for backups, recovery, or creating new volumes.
5. **Encryption:** EBS supports encryption of data at rest, in transit, and during snapshots, ensuring data security and compliance.
6. **High Availability and Durability:** EBS volumes are automatically replicated within their Availability Zone to protect against hardware failures, offering high availability and durability.

## Common Use Cases

- **Databases:** Running databases like MySQL, PostgreSQL, Oracle, or SQL Server that require high-performance storage.
- **Enterprise Applications:** Hosting enterprise applications such as SAP, Microsoft SharePoint, and others.
- **Big Data Analytics:** Storing and processing large datasets for analytics purposes.
- **Content Management Systems:** Running CMS platforms like WordPress, Drupal, or Joomla with persistent storage needs.

---

## Example: Launching an EC2 Instance with an EBS Volume

The following example walks through launching an EC2 instance and attaching an EBS volume to it using the AWS Management Console.

### Step 1: Launch an EC2 Instance

1. **Navigate to the EC2 Dashboard:**
   - Log in to your AWS Management Console.
   - Go to the **EC2** service.
2. **Launch Instance:**
   - Click on the **Launch Instance** button.
   - **Choose an Amazon Machine Image (AMI):** Select an AMI, such as Amazon Linux 2.
   - **Choose an Instance Type:** Select an instance type, e.g., `t2.micro`.
   - **Configure Instance Details:** Set the number of instances, network settings, etc.
   - **Add Storage:** By default, an EBS volume (e.g., 8 GB `gp2`) is attached. You can modify this or add additional volumes.
   - **Add Tags:** (Optional) Add tags for identification.
   - **Configure Security Group:** Set up firewall rules.
   - **Review and Launch:** Review your settings and launch the instance.

### Step 2: Create and Attach an Additional EBS Volume

1. **Create an EBS Volume:**
   - In the EC2 Dashboard, navigate to **Elastic Block Store** > **Volumes**.
   - Click on **Create Volume**.
   - Specify volume details:
     - **Size:** e.g., 20 GB.
     - **Volume Type:** e.g., `gp3`.
     - **Availability Zone:** Must be the same as your EC2 instance.
   - Click **Create Volume**.
2. **Attach the EBS Volume to the EC2 Instance:**
   - After creating the volume, select it from the list.
   - Click on **Actions** > **Attach Volume**.
   - **Specify Instance:** Choose the EC2 instance you launched earlier.
   - **Device Name:** e.g., `/dev/sdf` or `/dev/xvdf`.
   - Click **Attach**.

### Step 3: Configure the EBS Volume on the EC2 Instance

1. **Connect to Your EC2 Instance via SSH:**

   ```bash
   ssh -i /path/to/your-key-pair.pem ec2-user@your-instance-public-dns
   ```

2. **List Available Disks:**

   ```bash
   lsblk
   ```

   You should see the newly attached volume, e.g., `/dev/xvdf`.

3. **Create a Filesystem on the EBS Volume:**

   ```bash
   sudo mkfs -t ext4 /dev/xvdf
   ```

4. **Create a Mount Point:**

   ```bash
   sudo mkdir /mnt/data
   ```

5. **Mount the EBS Volume:**

   ```bash
   sudo mount /dev/xvdf /mnt/data
   ```

6. **Verify the Mount:**

   ```bash
   df -h
   ```

   You should see `/dev/xvdf` mounted at `/mnt/data`.

7. **Persist the Mount After Reboot (Optional):**

   Get the UUID of the volume:

   ```bash
   sudo blkid /dev/xvdf
   ```

   Edit the `/etc/fstab` file:

   ```bash
   sudo nano /etc/fstab
   ```

   Add the following line (replace `your-volume-uuid` with your volume's actual UUID):

   ```
   UUID=your-volume-uuid /mnt/data ext4 defaults,nofail 0 2
   ```

   Save and exit.

### Step 4: Utilize the EBS Volume

Now you can use the mounted EBS volume to store data. For example:

```bash
# Create a test file
echo "Hello, EBS!" | sudo tee /mnt/data/hello.txt

# Verify the file
cat /mnt/data/hello.txt
```

---

## Conclusion

Amazon EBS is a versatile and reliable block storage service that integrates seamlessly with EC2 instances, providing persistent and scalable storage solutions for a wide range of applications. Its various volume types cater to different performance and cost requirements, making it suitable for everything from small-scale projects to enterprise-level deployments.

The example above demonstrates the basic steps to launch an EC2 instance, create an EBS volume, attach it, and configure it for use. This setup is fundamental for applications that require durable and high-performance storage in the AWS cloud.
