import 'dart:convert';
import 'dart:io';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:image_picker/image_picker.dart';
import 'package:geolocator/geolocator.dart';
import '../../providers/api_providers.dart';
import '../../providers/delivery_provider.dart';
import '../../providers/partner_provider.dart';

class ProofOfDeliveryScreen extends ConsumerStatefulWidget {
  final String deliveryId;

  const ProofOfDeliveryScreen({super.key, required this.deliveryId});

  @override
  ConsumerState<ProofOfDeliveryScreen> createState() => _ProofOfDeliveryScreenState();
}

class _ProofOfDeliveryScreenState extends ConsumerState<ProofOfDeliveryScreen> {
  final _notesController = TextEditingController();
  String? _photoPath;
  bool _submitting = false;

  @override
  void dispose() {
    _notesController.dispose();
    super.dispose();
  }

  Future<void> _pickPhoto(ImageSource source) async {
    final picker = ImagePicker();
    final x = await picker.pickImage(source: source, maxWidth: 1200, imageQuality: 85);
    if (x != null) setState(() => _photoPath = x.path);
  }

  Future<String?> _photoToBase64() async {
    if (_photoPath == null) return null;
    try {
      final file = File(_photoPath!);
      if (!await file.exists()) return null;
      final bytes = await file.readAsBytes();
      return base64Encode(bytes);
    } catch (_) {
      return null;
    }
  }

  Future<void> _submit() async {
    setState(() => _submitting = true);
    try {
      Map<String, dynamic>? location;
      try {
        final pos = await Geolocator.getCurrentPosition(
          locationSettings: const LocationSettings(accuracy: LocationAccuracy.medium),
        );
        location = {'lat': pos.latitude, 'lng': pos.longitude};
        final partnerId = await ref.read(deliveryPartnerIdProvider.future);
        if (partnerId != null) {
          final service = ref.read(deliveryServiceProvider);
          await service.updatePartnerLocation(
            partnerId: partnerId,
            lat: pos.latitude,
            lng: pos.longitude,
          );
        }
      } catch (_) {}
      final notes = _notesController.text.trim();
      final proofBase64 = await _photoToBase64();
      final service = ref.read(deliveryServiceProvider);
      final res = await service.updateDeliveryStatus(
        deliveryId: widget.deliveryId,
        status: 'DELIVERED',
        location: location,
        notes: notes.isEmpty && proofBase64 == null ? 'Delivered' : (notes.isNotEmpty ? notes : 'Proof photo attached'),
        proofPhotoBase64: proofBase64,
      );
      if (!mounted) return;
      if (res.success) {
        ref.invalidate(deliveryDetailProvider(widget.deliveryId));
        ref.invalidate(myDeliveriesProvider);
        context.pop();
        ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Marked as delivered')));
      } else {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text(res.message ?? 'Failed'), backgroundColor: Colors.red),
        );
      }
    } finally {
      if (mounted) setState(() => _submitting = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Proof of delivery'),
        leading: IconButton(
          icon: const Icon(Icons.close),
          onPressed: () => context.pop(),
        ),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(24),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Text(
              'Add proof before marking as delivered (optional but recommended).',
              style: Theme.of(context).textTheme.bodyMedium?.copyWith(color: Colors.grey.shade700),
            ),
            const SizedBox(height: 24),
            Text('Photo', style: Theme.of(context).textTheme.titleSmall),
            const SizedBox(height: 8),
            if (_photoPath != null && File(_photoPath!).existsSync())
              Stack(
                alignment: Alignment.topRight,
                children: [
                  ClipRRect(
                    borderRadius: BorderRadius.circular(12),
                    child: Image.file(
                      File(_photoPath!),
                      height: 180,
                      width: double.infinity,
                      fit: BoxFit.cover,
                    ),
                  ),
                  IconButton(
                    icon: const Icon(Icons.close),
                    onPressed: () => setState(() => _photoPath = null),
                    style: IconButton.styleFrom(backgroundColor: Colors.black54),
                  ),
                ],
              )
            else
              Row(
                children: [
                  OutlinedButton.icon(
                    onPressed: () => _pickPhoto(ImageSource.camera),
                    icon: const Icon(Icons.camera_alt),
                    label: const Text('Camera'),
                  ),
                  const SizedBox(width: 12),
                  OutlinedButton.icon(
                    onPressed: () => _pickPhoto(ImageSource.gallery),
                    icon: const Icon(Icons.photo_library),
                    label: const Text('Gallery'),
                  ),
                ],
              ),
            const SizedBox(height: 24),
            Text('Notes (optional)', style: Theme.of(context).textTheme.titleSmall),
            const SizedBox(height: 8),
            TextField(
              controller: _notesController,
              decoration: const InputDecoration(
                hintText: 'e.g. Handed to customer at door',
                border: OutlineInputBorder(),
              ),
              maxLines: 2,
            ),
            const SizedBox(height: 32),
            FilledButton(
              onPressed: _submitting ? null : _submit,
              style: FilledButton.styleFrom(
                padding: const EdgeInsets.symmetric(vertical: 16),
              ),
              child: _submitting
                  ? const SizedBox(
                      height: 24,
                      width: 24,
                      child: CircularProgressIndicator(strokeWidth: 2),
                    )
                  : const Text('Mark as delivered'),
            ),
          ],
        ),
      ),
    );
  }
}
