import 'dart:io';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:image_picker/image_picker.dart';
import '../../providers/kyc_onboarding_provider.dart';
import '../../providers/store_provider.dart';

class KycOnboardingScreen extends ConsumerWidget {
  const KycOnboardingScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final state = ref.watch(kycOnboardingProvider);
    final notifier = ref.read(kycOnboardingProvider.notifier);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Complete KYC'),
        leading: state.currentStep > 0
            ? IconButton(
                icon: const Icon(Icons.arrow_back),
                onPressed: () => notifier.previousStep(),
              )
            : IconButton(
                icon: const Icon(Icons.close),
                onPressed: () => context.pop(),
              ),
      ),
      body: Column(
        children: [
          _StepIndicator(currentStep: state.currentStep),
          Expanded(
            child: SingleChildScrollView(
              padding: const EdgeInsets.all(24),
              child: state.currentStep == 0
                  ? _Step1BasicDetails(state: state, notifier: notifier)
                  : state.currentStep == 1
                      ? _Step2BusinessType(state: state, notifier: notifier)
                      : state.currentStep == 2
                          ? _Step3Documents(state: state, notifier: notifier)
                          : _Step4Review(state: state, notifier: notifier),
            ),
          ),
          if (state.submitError != null)
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 24),
              child: Text(
                state.submitError!,
                style: TextStyle(color: Theme.of(context).colorScheme.error, fontSize: 12),
              ),
            ),
          Padding(
            padding: const EdgeInsets.all(24),
            child: Row(
              children: [
                if (state.currentStep > 0)
                  OutlinedButton(
                    onPressed: state.isSubmitting ? null : () => notifier.previousStep(),
                    child: const Text('Back'),
                  ),
                const SizedBox(width: 12),
                Expanded(
                  child: FilledButton(
                    onPressed: state.isSubmitting
                        ? null
                        : () async {
                            if (state.currentStep < 3) {
                              notifier.nextStep();
                            } else {
                              final ok = await notifier.submit();
                              if (context.mounted && ok) {
                                ref.invalidate(retailerStoreProvider);
                                context.pop();
                                ScaffoldMessenger.of(context).showSnackBar(
                                  const SnackBar(content: Text('KYC submitted. We will review shortly.')),
                                );
                              }
                            }
                          },
                    child: state.isSubmitting
                        ? const SizedBox(
                            height: 20,
                            width: 20,
                            child: CircularProgressIndicator(strokeWidth: 2),
                          )
                        : Text(state.currentStep < 3 ? 'Next' : 'Submit'),
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

class _StepIndicator extends StatelessWidget {
  final int currentStep;

  const _StepIndicator({required this.currentStep});

  @override
  Widget build(BuildContext context) {
    const steps = ['Details', 'Business', 'Documents', 'Review'];
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 16),
      child: Row(
        children: List.generate(steps.length * 2 - 1, (i) {
          if (i.isOdd) {
            return Expanded(
              child: Divider(
                color: currentStep > i ~/ 2 ? Theme.of(context).colorScheme.primary : Colors.grey.shade300,
              ),
            );
          }
          final stepIndex = i ~/ 2;
          final active = currentStep == stepIndex;
          final done = currentStep > stepIndex;
          return Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              CircleAvatar(
                radius: 16,
                backgroundColor: done
                    ? Theme.of(context).colorScheme.primary
                    : active
                        ? Theme.of(context).colorScheme.primary
                        : Colors.grey.shade300,
                child: done
                    ? Icon(Icons.check, size: 18, color: Theme.of(context).colorScheme.onPrimary)
                    : Text(
                        '${stepIndex + 1}',
                        style: TextStyle(
                          color: active ? Theme.of(context).colorScheme.onPrimary : Colors.grey.shade600,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
              ),
              const SizedBox(height: 4),
              Text(
                steps[stepIndex],
                style: Theme.of(context).textTheme.labelSmall?.copyWith(
                      color: active || done ? Theme.of(context).colorScheme.primary : Colors.grey.shade600,
                    ),
              ),
            ],
          );
        }),
      ),
    );
  }
}

class _Step1BasicDetails extends StatelessWidget {
  final KycOnboardingState state;
  final KycOnboardingNotifier notifier;

  const _Step1BasicDetails({required this.state, required this.notifier});

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        Text('Business & contact details', style: Theme.of(context).textTheme.titleMedium),
        const SizedBox(height: 16),
        TextFormField(
          initialValue: state.businessName,
          decoration: const InputDecoration(labelText: 'Business / Store name'),
          onChanged: (v) => notifier.updateBasicDetails(businessName: v),
        ),
        const SizedBox(height: 12),
        TextFormField(
          initialValue: state.ownerName,
          decoration: const InputDecoration(labelText: 'Owner name'),
          onChanged: (v) => notifier.updateBasicDetails(ownerName: v),
        ),
        const SizedBox(height: 12),
        TextFormField(
          initialValue: state.phone,
          decoration: const InputDecoration(labelText: 'Phone'),
          keyboardType: TextInputType.phone,
          onChanged: (v) => notifier.updateBasicDetails(phone: v),
        ),
        const SizedBox(height: 12),
        TextFormField(
          initialValue: state.email,
          decoration: const InputDecoration(labelText: 'Email'),
          keyboardType: TextInputType.emailAddress,
          onChanged: (v) => notifier.updateBasicDetails(email: v),
        ),
        const SizedBox(height: 16),
        Text('Store address', style: Theme.of(context).textTheme.titleSmall),
        const SizedBox(height: 8),
        TextFormField(
          initialValue: state.addressLine1,
          decoration: const InputDecoration(labelText: 'Address line 1'),
          onChanged: (v) => notifier.updateBasicDetails(addressLine1: v),
        ),
        const SizedBox(height: 12),
        TextFormField(
          initialValue: state.addressLine2,
          decoration: const InputDecoration(labelText: 'Address line 2 (optional)'),
          onChanged: (v) => notifier.updateBasicDetails(addressLine2: v),
        ),
        const SizedBox(height: 12),
        Row(
          children: [
            Expanded(
              flex: 2,
              child: TextFormField(
                initialValue: state.city,
                decoration: const InputDecoration(labelText: 'City'),
                onChanged: (v) => notifier.updateBasicDetails(city: v),
              ),
            ),
            const SizedBox(width: 12),
            Expanded(
              child: TextFormField(
                initialValue: state.state,
                decoration: const InputDecoration(labelText: 'State'),
                onChanged: (v) => notifier.updateBasicDetails(addressState: v),
              ),
            ),
          ],
        ),
        const SizedBox(height: 12),
        TextFormField(
          initialValue: state.pincode,
          decoration: const InputDecoration(labelText: 'Pincode'),
          keyboardType: TextInputType.number,
          onChanged: (v) => notifier.updateBasicDetails(pincode: v),
        ),
      ],
    );
  }
}

class _Step2BusinessType extends StatelessWidget {
  final KycOnboardingState state;
  final KycOnboardingNotifier notifier;

  const _Step2BusinessType({required this.state, required this.notifier});

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        Text('Business type', style: Theme.of(context).textTheme.titleMedium),
        const SizedBox(height: 16),
        DropdownButtonFormField<String>(
          value: state.businessType,
          decoration: const InputDecoration(labelText: 'Type of store'),
          items: KycOnboardingState.businessTypes
              .map((e) => DropdownMenuItem(value: e, child: Text(e)))
              .toList(),
          onChanged: (v) => notifier.updateBusinessType(businessType: v),
        ),
        const SizedBox(height: 20),
        Text('Delivery preference', style: Theme.of(context).textTheme.titleSmall),
        const SizedBox(height: 8),
        DropdownButtonFormField<String>(
          value: state.deliveryPreference,
          decoration: const InputDecoration(labelText: 'Who delivers orders?'),
          items: KycOnboardingState.deliveryPreferences
              .map((e) => DropdownMenuItem(value: e, child: Text(e)))
              .toList(),
          onChanged: (v) => notifier.updateBusinessType(deliveryPreference: v),
        ),
      ],
    );
  }
}

class _Step3Documents extends StatelessWidget {
  final KycOnboardingState state;
  final KycOnboardingNotifier notifier;

  const _Step3Documents({required this.state, required this.notifier});

  Future<void> _pickImage(ImageSource source, void Function(String?) setPath) async {
    final picker = ImagePicker();
    final x = await picker.pickImage(source: source, maxWidth: 1200, imageQuality: 85);
    if (x != null) setPath(x.path);
  }

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        Text('Upload documents', style: Theme.of(context).textTheme.titleMedium),
        const SizedBox(height: 8),
        Text(
          'PAN and cancelled cheque are required. GST is optional for small retailers.',
          style: Theme.of(context).textTheme.bodySmall?.copyWith(color: Colors.grey.shade600),
        ),
        const SizedBox(height: 20),
        _DocTile(
          title: 'PAN card',
          required: true,
          imagePath: state.panImagePath,
          onTap: () async {
            await _pickImage(ImageSource.gallery, notifier.setPanImage);
          },
          onClear: () => notifier.setPanImage(null),
        ),
        const SizedBox(height: 16),
        _DocTile(
          title: 'GST certificate (optional)',
          required: false,
          imagePath: state.gstImagePath,
          onTap: () async {
            await _pickImage(ImageSource.gallery, notifier.setGstImage);
          },
          onClear: () => notifier.setGstImage(null),
        ),
        const SizedBox(height: 16),
        _DocTile(
          title: 'Cancelled cheque',
          required: true,
          imagePath: state.cancelledChequePath,
          onTap: () async {
            await _pickImage(ImageSource.gallery, notifier.setCancelledChequeImage);
          },
          onClear: () => notifier.setCancelledChequeImage(null),
        ),
      ],
    );
  }
}

class _DocTile extends StatelessWidget {
  final String title;
  final bool required;
  final String? imagePath;
  final VoidCallback onTap;
  final VoidCallback onClear;

  const _DocTile({
    required this.title,
    required this.required,
    required this.imagePath,
    required this.onTap,
    required this.onClear,
  });

  @override
  Widget build(BuildContext context) {
    return Card(
      child: ListTile(
        title: Row(
          children: [
            Text(title),
            if (required) Text(' *', style: TextStyle(color: Theme.of(context).colorScheme.error)),
          ],
        ),
        subtitle: imagePath != null
            ? Row(
                children: [
                  if (File(imagePath!).existsSync())
                    ClipRRect(
                      borderRadius: BorderRadius.circular(8),
                      child: Image.file(File(imagePath!), height: 48, width: 48, fit: BoxFit.cover),
                    ),
                  const SizedBox(width: 8),
                  Text('Uploaded', style: TextStyle(color: Colors.green.shade700)),
                ],
              )
            : const Text('Tap to upload'),
        trailing: imagePath != null
            ? IconButton(icon: const Icon(Icons.close), onPressed: onClear)
            : const Icon(Icons.upload_file),
        onTap: onTap,
      ),
    );
  }
}

class _Step4Review extends StatelessWidget {
  final KycOnboardingState state;
  final KycOnboardingNotifier notifier;

  const _Step4Review({required this.state, required this.notifier});

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        Text('Review and submit', style: Theme.of(context).textTheme.titleMedium),
        const SizedBox(height: 16),
        _ReviewRow(label: 'Business', value: state.businessName),
        _ReviewRow(label: 'Owner', value: state.ownerName),
        _ReviewRow(label: 'Phone', value: state.phone),
        _ReviewRow(label: 'Email', value: state.email),
        _ReviewRow(
          label: 'Address',
          value: '${state.addressLine1}, ${state.city}, ${state.state} ${state.pincode}',
        ),
        _ReviewRow(label: 'Business type', value: state.businessType),
        _ReviewRow(label: 'Delivery', value: state.deliveryPreference),
        const SizedBox(height: 12),
        _ReviewRow(label: 'PAN', value: state.panImagePath != null ? 'Uploaded' : 'Missing'),
        _ReviewRow(label: 'GST', value: state.gstImagePath != null ? 'Uploaded' : 'Optional'),
        _ReviewRow(label: 'Cancelled cheque', value: state.cancelledChequePath != null ? 'Uploaded' : 'Missing'),
      ],
    );
  }
}

class _ReviewRow extends StatelessWidget {
  final String label;
  final String value;

  const _ReviewRow({required this.label, required this.value});

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          SizedBox(width: 100, child: Text(label, style: Theme.of(context).textTheme.bodySmall)),
          Expanded(child: Text(value)),
        ],
      ),
    );
  }
}
